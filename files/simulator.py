import os
import ltspice # pip3 install ltspice

ltspice_exe = "bash ../ltspice.sh"
ltspice_dir = "./files/"

def set_ltspice(exe, dir):
    global ltspice_exe
    global ltspice_dir
    ltspice_exe = exe
    ltspice_dir = dir

def convert_ltspice_sch_to_netlist(filename="my_crossbar_wrapper"):
    # ltspice netlist batch command
    os.system(f'{ltspice_exe} -netlist {ltspice_dir}/{filename}.asc')

def simulate_netlist(wordline, bitline, io, netlist="my_crossbar_wrapper", tmp_id=1):
    row = wordline
    col = bitline

    # Open up template
    with open(netlist + '.net', "r") as f:
        content = f.read()

    # Sub in all the values
    for r in range(wordline):
        label = f"<WORD{r}>"
        value = str(int(io['WORD'][r]))
        content = content.replace(label, value)

    for c in range(bitline):
        label = f"<BIT{c}>"
        value = str(int(io['BIT'][c]))
        content = content.replace(label, value)

    cba_params = []
    for c in range(bitline):
        for r in range(wordline):
            label = f"G{r}.{c}"
            value = str(int(io['G'][r][c]))
            cba_params.append(f"{label}={value}")
    content = content.replace("<CBA1_PARAMS>", " ".join(cba_params))

    # Write to file
    tmp_filename = f"{netlist}_tmp{tmp_id}"
    with open(tmp_filename + '.net', "w") as f:
        f.write(content)

    # Run simulation
    os.system(f'{ltspice_exe} -nowine -Run -b {ltspice_dir}/{tmp_filename}.net')
    print("> Simulation done")

    # Read simulation
    l = ltspice.Ltspice(tmp_filename + '.raw')
    l.parse() 

    # time = l.get_time()
    # plt.plot(time, V_source)
    # plt.plot(time, V_cap)
    # plt.show()

    word_current = []
    for r in range(row):
        label = f"I(V.WORD{r})"
        data = l.get_data(label)[-1] # flowing into source
        word_current.append(data)

    bit_current = []
    for c in range(col):
        label = f"I(V.BIT{c})"
        data = l.get_data(label)[-1] # flowing into source
        bit_current.append(data)

    return {
        'word_current': word_current,
        'bit_current': bit_current
    }

if __name__ == "__main__":
    import code
    code.interact(local=locals())
