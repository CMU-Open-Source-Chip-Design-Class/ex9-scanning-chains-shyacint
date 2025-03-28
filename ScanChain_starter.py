import copy
import cocotb
from cocotb.triggers import Timer


# Make sure to set FILE_NAME
# to the filepath of the .log
# file you are working with
CHAIN_LENGTH = -1
FILE_NAME    = "/home/user/18_624/exercises/ex9-scanning-chains-shyacint/adder/adder.log"



# Holds information about a register
# in your design.

################
# DO NOT EDIT!!!
################
class Register:

    def __init__(self, name) -> None:
        self.name = name            # Name of register, as in .log file
        self.size = -1              # Number of bits in register

        self.bit_list = list()      # Set this to the register's contents, if you want to
        self.index_list = list()    # List of bit mappings into chain. See handout

        self.first = -1             # LSB mapping into scan chain
        self.last  = -1             # MSB mapping into scan chain


# Holds information about the scan chain
# in your design.
        
################
# DO NOT EDIT!!!
################
class ScanChain:

    def __init__(self) -> None:
        self.registers = dict()     # Dictionary of Register objects, indexed by 
                                    # register name
        
        self.chain_length = 0       # Number of FFs in chain


# Sets up a new ScanChain object
# and returns it

################     
# DO NOT EDIT!!!
################
def setup_chain(filename):

    scan_chain = ScanChain()

    f = open(filename, "r")
    for line in f:
        linelist = line.split()
        index, name, bit = linelist[0], linelist[1], linelist[2]

        if name not in scan_chain.registers:
            reg = Register(name)
            reg.index_list.append((int(bit), int(index)))
            scan_chain.registers[name] = reg

        else:
            scan_chain.registers[name].index_list.append((int(bit), int(index)))
        
    f.close()

    for name in scan_chain.registers:
        cur_reg = scan_chain.registers[name]
        cur_reg.index_list.sort()
        new_list = list()
        for tuple in cur_reg.index_list:
            new_list.append(tuple[1])
        
        cur_reg.index_list = new_list
        cur_reg.bit_list   = [0] * len(new_list)
        cur_reg.size = len(new_list)
        cur_reg.first = new_list[0]
        cur_reg.last  = new_list[-1]
        scan_chain.chain_length += len(cur_reg.index_list)

    return scan_chain


# Prints info of given Register object

################
# DO NOT EDIT!!!
################
def print_register(reg):
    print("------------------")
    print(f"NAME:    {reg.name}")
    print(f"BITS:    {reg.bit_list}")
    print(f"INDICES: {reg.index_list}")
    print("------------------")


# Prints info of given ScanChain object

################   
# DO NOT EDIT!!!
################
def print_chain(chain):
    print("---CHAIN DISPLAY---\n")
    print(f"CHAIN SIZE: {chain.chain_length}\n")
    print("REGISTERS: \n")
    for name in chain.registers:
        cur_reg = chain.registers[name]
        print_register(cur_reg)



#-------------------------------------------------------------------

# This function steps the clock once.
    
# Hint: Use the Timer() builtin function
async def step_clock(dut):
    dut.clock = True
    await Timer(10, units='ns')
    dut.clock = False
    await Timer(10, units='ns')
    

#-------------------------------------------------------------------

# This function places a bit value inside FF of specified index.
        
# Hint: How many clocks would it take for value to reach
#       the specified FF?
        
async def input_chain_single(dut, bit, ff_index):
    dut.scan_en = True
    dut.scan_in = bit
    for cycle in range(ff_index):
        await step_clock(dut)
    dut.scan_en = False
        
async def input_chain(dut, bit_list, ff_index):
    dut.scan_en = True
    for bit in reversed(bit_list):
        scan_in = bit
        step_clock(dut)
    dut.scan_en = False

    # biases the idx so it is in the right FF
    for cycle in range(ff_index):
        step_clock(dut)
        
async def output_chain_single(dut, ff_index):
    dut.scan_en = True
    dut.scan_in = bit
    for cycle in range(CHAIN_LENGTH - ff_index):
        await step_clock(dut)
    dut.scan_en = False
    return dut.scan_out   
        
async def output_chain(dut, ff_index, output_length):
    ignore_cycles = CHAIN_LENGTH - (output_length + ff_index)
    # clearing out the values we don't care about 
    for _ in range(ignore_cycles):
        step_clock(dut)
    
    scan_values = []
    for _ in range(output_length):
        scan_values.append(dut.scan_out)

    return scan_values.reverse()

#-----------------------------------------------

# Your main testbench function

@cocotb.test()
async def test(dut):

    global CHAIN_LENGTH
    global FILE_NAME        # Make sure to edit this guy
                            # at the top of the file

    # Setup the scan chain object
    chain = setup_chain(FILE_NAME)

    ######################
    # TODO: YOUR CODE HERE 
    ######################

