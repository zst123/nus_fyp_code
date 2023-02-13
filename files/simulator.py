import os
import ltspice # pip3 install ltspice
import my_hspice

use_spice = 'ltspice'
ltspice_exe = "bash ../ltspice.sh"
ltspice_dir = "./files/"
hspice_exe = "hspice"
hspice_dir = "./files/"

def set_ltspice(exe, dir):
    global use_spice
    global ltspice_exe
    global ltspice_dir
    use_spice = 'ltspice'
    ltspice_exe = exe
    ltspice_dir = dir

def set_hspice(exe, dir):
    global use_spice
    global hspice_exe
    global hspice_dir
    use_spice = 'hspice'
    hspice_exe = exe
    hspice_dir = dir

def convert_ltspice_sch_to_netlist(filename="my_crossbar_wrapper"):
    # ltspice netlist batch command
    os.system(f'{ltspice_exe} -netlist {ltspice_dir}/{filename}.asc')

    # Modify to be compatible with hspice
    with open(f'{filename}.net', 'r') as f:
        content = f.read()

    with open(f'{filename}.hspice.net', 'w') as f:
        content = content.replace('params: ', '')
        content = content.replace('{', "'").replace('}', "'")
        content = content.replace('.backanno', ".OPTIONS POST=2 nomod")
        f.write(content)

def simulate_netlist(wordline, bitline, io, netlist="my_crossbar_wrapper", tmp_id=1):
    row = wordline
    col = bitline

    # Open up template
    if use_spice == 'ltspice':
        filename_netlist = netlist + '.net'
    elif use_spice == 'hspice':
        filename_netlist = netlist + '.hspice.net'

    with open(filename_netlist, "r") as f:
        content = f.read()

    # Sub in all the values
    content = handle_param_sub(content, wordline, bitline, io)

    # Write to file
    tmp_filename = f"{netlist}_tmp{tmp_id}"
    if use_spice == 'ltspice':
        filename_tmp_netlist = tmp_filename + '.net'
    elif use_spice == 'hspice':
        filename_tmp_netlist = tmp_filename + '.hspice.net'
    with open(filename_tmp_netlist, "w") as f:
        f.write(content)

    # Run simulation
    if use_spice == 'ltspice':
        os.system(f'{ltspice_exe} -nowine -Run -b {ltspice_dir}/{filename_tmp_netlist}')
        print("> Simulation done using ltspice")
    elif use_spice == 'hspice':
        os.system(f'{hspice_exe} {hspice_dir}/{filename_tmp_netlist}')
        print("> Simulation done using hspice")

    # Read simulation
    if use_spice == 'ltspice':
        l = ltspice.Ltspice(tmp_filename + '.raw')
        l.parse()
        def _get_data(label):
            return l.get_data(label)
        print("> Parsing ltspice results")
    elif use_spice == 'hspice':
        h = my_hspice.read_hspice_tr(filename=tmp_filename + '.hspice.tr0')
        def _get_data(label):
            return h[label.lower()]
        print("> Parsing hspice results")

    # time = l.get_time()
    # plt.plot(time, V_source)
    # plt.plot(time, V_cap)
    # plt.show()

    return handle_result_sub(wordline, bitline, _get_data)

def handle_result_sub(wordline, bitline, get_data):
    word_current = []
    for r in range(wordline):
        label = f"I(V.WORD{r})"
        data = get_data(label)[-1] # flowing into source
        word_current.append(data)

    bit_current = []
    for c in range(bitline):
        label = f"I(V.BIT{c})"
        data = get_data(label)[-1] # flowing into source
        bit_current.append(data)

    return {
        'word_current': word_current,
        'bit_current': bit_current
    }

def handle_param_sub(content, wordline, bitline, io):
    for r in range(wordline):
        label = f"<WORD{r}>"
        value = str(io['WORD'][r])
        content = content.replace(label, value)

    for c in range(bitline):
        label = f"<BIT{c}>"
        value = str(io['BIT'][c])
        content = content.replace(label, value)

    cba_params = []
    for c in range(bitline):
        for r in range(wordline):
            label = f"G{r}.{c}"
            value = str(int(io['G'][r][c]))
            cba_params.append(f"{label}={value}")
    content = content.replace("<CBA1_PARAMS>", " ".join(cba_params))
    return content

if __name__ == "__main__":
    import code
    code.interact(local=locals())
