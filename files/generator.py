import os
from datetime import datetime

def getdate():
    now = datetime.now() # current date and time
    date_time = now.strftime("%d/%b/%Y, %H:%M:%S")
    return date_time

def generate_cell(resistance_states, cell_subcircuit="cell_subcircuit"):
    # .asc file

    # table() syntax is supported in LTspice, Hspice
    items = []
    for index, value in enumerate(resistance_states):
        items.append(str(index))
        items.append(str(value))
    lookup_table = "table(state," + (",".join(items)) + ")"

    content = f"""Version 4
SHEET 1 880 680
FLAG 192 112 1
IOPIN 192 112 BiDir
FLAG 192 192 2
IOPIN 192 192 BiDir
SYMBOL res 176 96 R0
SYMATTR InstName R1
SYMATTR Value {{resistance}}
TEXT 192 48 Center 1 !.param resistance={lookup_table}
"""
    with open(cell_subcircuit + '.asc', "w") as f:
        f.write(content)

    # .asy file
    content = """Version 4
SymbolType BLOCK
LINE Normal 16 32 16 16
LINE Normal 16 80 16 96
RECTANGLE Normal 24 80 8 32
WINDOW 0 16 64 Bottom 2
PIN 16 16 NONE 8
PINATTR PinName 1
PINATTR SpiceOrder 1
PIN 16 96 NONE 8
PINATTR PinName 2
PINATTR SpiceOrder 2
"""
    with open(cell_subcircuit + '.asy', "w") as f:
        f.write(content)

def generate_cba(wordline=30, bitline=30, filename="crossbar_subcircuit", cell_subcircuit="cell_subcircuit", wrapper=None):
    row = wordline
    col = bitline
    entries = []

    # Function helpers
    def add_voltage_with_gnd(name, value, x, y):
        entries.append(f"SYMBOL voltage {int(x)} {int(y)} R0")
        entries.append(f"SYMATTR InstName V.{name}")
        entries.append(f"SYMATTR Value {value}")
        entries.append(f"FLAG {int(x)} {int(y+16)} {name}")
        entries.append(f"FLAG {int(x)} {int(y+96)} 0")

    def add_flag(name, x, y):
        entries.append(f"FLAG {int(x)} {int(y)} {name}")
        entries.append(f"IOPIN {int(x)} {int(y)} BiDir")

    def add_text(text, x, y, size):
        entries.append(f"TEXT {int(x)} {int(y)} Left {size} ;{text}")

    def add_resistor(name, value, x, y, rotate=0):
        entries.append(f"SYMBOL res {int(x)} {int(y)} R{int(rotate)}")
        entries.append(f"SYMATTR InstName {name}")
        entries.append(f"SYMATTR Value {value}")

    def add_cell_subcircuit(name, value, x, y, rotate=0):
        entries.append(f"SYMBOL {cell_subcircuit} {int(x)} {int(y)} R{int(rotate)}")
        entries.append(f"SYMATTR InstName {name}")
        entries.append(f"SYMATTR SpiceLine state={value}")

    def add_wire(x1, y1, x2, y2):
        entries.append(f"WIRE {int(x1)} {int(y1)} {int(x2)} {int(y2)}")

    def add_pin(name, spice_order, x, y, rotate, offset=8):
        entries.append(f"PIN {int(x)} {int(y)} {rotate} {int(offset)}")
        entries.append(f"PINATTR PinName {name}")
        entries.append(f"PINATTR SpiceOrder {spice_order}")

    #######################################
    # Generate Schematic
    #######################################
    entries.clear()
    entries.append("Version 4")
    entries.append("SHEET 1 880 680")
    entries.append("TEXT -64 -64 Right 2 !.tran 0m 1m 0m")
    
    # Add text comment
    text = f"Generated on {getdate()}"
    add_text(text, 0, -64, 3)
    
    # Draw resistor array
    GRID_X = 192
    GRID_Y = 120
    JOINER_X = -32
    for c in range(col):
        for r in range(row):
            label = f"G{r}.{c}"
            # add_resistor(name=label, value=f"<{label}>",
            #              x=c*GRID_X-16, y=r*GRID_Y-16, rotate = 0)
            add_cell_subcircuit(name=label, value=f"{{{label}}}",
                         x=c*GRID_X-16, y=r*GRID_Y-16, rotate = 0)

            # Wordline: Top Horizontal
            add_wire(x1=(c-1)*GRID_X, y1=r*GRID_Y,
                     x2=(c+0)*GRID_X, y2=r*GRID_Y)
            
            # Joiner: Bottom Horizontal
            add_wire(x1=c*GRID_X,          y1=r*GRID_Y+80,
                     x2=c*GRID_X+JOINER_X, y2=r*GRID_Y+80)

            # Bitline: Bottom Vertical
            add_wire(x1=c*GRID_X+JOINER_X, y1=(r+0)*GRID_Y+80,
                     x2=c*GRID_X+JOINER_X, y2=(r+1)*GRID_Y+80)

    # Add flag labels
    for r in range(row):
        label = f"WORD{r}"
        add_flag(name=label, x=(-1)*GRID_X, y=r*GRID_Y)
        # add_voltage_with_gnd(name=label, value=f"<{label}>",
        #                      x=r*GRID_X, y=-200)
    
    # Add flag labels
    for c in range(col):
        label = f"BIT{c}"
        add_flag(label, x=(c)*GRID_X+JOINER_X, y=(row)*GRID_Y+80)
        # add_voltage_with_gnd(name=label, value=f"<{label}>",
        #                      x=c*GRID_X, y=-400)
    
    # Write to file
    with open(filename + '.asc', "w") as f:
        content = '\n'.join(entries)
        f.write(content)

    #######################################
    # Generate Subcircuit Symbol
    #######################################
    entries.clear()
    entries.append("Version 4")
    entries.append("SymbolType BLOCK")

    # Draw symbol pins
    GRID_X = 16*2
    GRID_Y = 16*2
    OFFSET_X = -1*16*5
    OFFSET_Y = +1*16*5
    for c in range(col):
        label = f"BIT{c}"
        add_pin(label, x=c*GRID_X, y=OFFSET_Y, spice_order=c+1, rotate="VLEFT")

    for r in range(row):
        label = f"WORD{r}"
        add_pin(label, x=OFFSET_X, y=-r*GRID_Y, spice_order=r+col+1, rotate="LEFT")

    entries.append(f"RECTANGLE Normal {(col+1)*GRID_X} {-(row+1)*GRID_Y} {OFFSET_X} {OFFSET_Y}")

    # Write to file
    with open(filename + '.asy', "w") as f:
        content = '\n'.join(entries)
        f.write(content)

    #######################################
    # Generate Wrapper Template
    #######################################
    if wrapper:
        entries.clear()
        entries.append("Version 4")
        entries.append("SHEET 1 880 680")
        entries.append("TEXT 64 -64 LEFT 2 !.tran 0m 1m 0m")

        # Crossbar with labels
        entries.append(f"SYMBOL {filename} 0 0 R0")
        entries.append(f"SYMATTR InstName CBA1")
        entries.append(f"SYMATTR SpiceLine <CBA1_PARAMS>")

        # Add net labels to crossbar array
        for c in range(col):
            label = f"BIT{c}"
            add_flag(label, x=c*GRID_X, y=OFFSET_Y)

        for r in range(row):
            label = f"WORD{r}"
            add_flag(label, x=OFFSET_X, y=-r*GRID_Y)

        # Add voltage sources
        GRID_V = 16*6
        for c in range(col):
            label = f"BIT{c}"
            add_voltage_with_gnd(name=label, value=f"<{label}>",
                                 x=c*GRID_V, y=600)

        for r in range(row):
            label = f"WORD{r}"
            add_flag(label, x=OFFSET_X, y=-r*GRID_Y)
            add_voltage_with_gnd(name=label, value=f"<{label}>",
                                 x=r*GRID_V, y=400)

        # Write to file
        with open(wrapper + '.asc', "w") as f:
            content = '\n'.join(entries)
            f.write(content)

if __name__ == "__main__":
    import code
    code.interact(local=locals())
