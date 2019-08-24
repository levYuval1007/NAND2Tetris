import sys
import os

# magic numbers
FIRST_SYMBOL_MEM = 16
NUM_OF_BITS = 16

# dictionaries
jmp_dict = {"JGT": "001", "JEQ": "010", "JGE": "011", "JLT": "100",
            "JNE": "101", "JLE": "110", "JMP": "111", "no_jump": "000"}

dest_dict = {"M": "001", "D": "010", "MD": "011", "A": "100", "AM": "101",
             "AD": "110", "AMD": "111", "no_address": "000"}

comp_dict = {"0": "110101010", "1": "110111111", "-1": "110111010",
             "D": "110001100", "A": "110110000", "M": "111110000",
             "!D": "110001101",
             "!A": "110110001", "!M": "111110001", "-D": "110001111",
             "-A": "110110011", "-M": "111110011", "D+1": "110011111", "A+1":
                 "110110111", "M+1": "111110111", "D-1": "110001110", "A-1":
                 "110110010", "M-1": "111110010", "D+A": "110000010",
             "A+D": "110000010", "M+D": "111000010",
             "D+M": "111000010", "D-A": "110010011", "D-M": "111010011", "A-D":
                 "110000111", "M-D": "111000111", "D&A": "110000000",
             "A&D": "110000000", "D&M": "111000000", "M&D": "111000000",
             "D|A": "110010101", "A|D": "110010101",
             "D|M": "111010101", "M|D": "111010101",
             "D<<": "010110000", "A<<": "010100000", "M<<": "011100000",
             "D>>": "010010000", "A>>": "010000000", "M>>": "011000000"}

symbol_dict = {"R0": "0", "R1": "1", "R2": "2", "R3": "3", "R4": "4",
               "R5": "5", "R6": "6", "R7": "7", "R8": "8", "R9": "9",
               "R10": "10", "R11": "11", "R12": "12", "R13": "13", "R14":
                   "14", "R15": "15", "SCREEN": "16384", "KBD": "24576",
               "SP": "0", "LCL": "1", "ARG": "2", "THIS": "3", "THAT": "4"}


def convert_a_inst(inst):
    """
    this method is converting an a instruction from string to bit.
    :param inst: a string representing the instruction, starts with @ (
    without comments).
    :return: the instruction on bit representation.
    """
    bin_inst = (bin(int(inst)))[2:]
    inst_to_return = ['0'] * NUM_OF_BITS
    inst_to_return[-(len(bin_inst)):] = bin_inst
    return ''.join(inst_to_return)


def convert_c_inst(inst):
    """
    this method is converting a c instruction from string to bit.
    :param inst: a string instruction without comments
    :return: the binary representation of the instruction
    """
    split_inst = inst.split(";")
    inst_to_return = ['1'] * NUM_OF_BITS
    if len(split_inst) == 1:  # if no jump
        inst_to_return[13:] = jmp_dict["no_jump"]
    else:
        inst_to_return[13:] = jmp_dict[split_inst[1]]

    comp_inst = split_inst[0]
    split_inst = comp_inst.split("=")

    if len(split_inst) == 2:  # address handling
        inst_to_return[10:13] = dest_dict[split_inst[0]]

    else:
        inst_to_return[10:13] = dest_dict["no_address"]

    inst_to_return[1:10] = comp_dict[split_inst[-1]]  # comp handling

    return ''.join(inst_to_return)  # returns a string representing the
    # instruction


def write_to_out(clean_code, file_name):
    """
    this function is writing all binary instructions to out file.
    :param clean_code: an array containing the given code lines without
    spaces, comments or label declaration
    :param file_name: the name of the out hack file
    """
    symbol_count = FIRST_SYMBOL_MEM  # first available address for new symbols
    with open(file_name, "w") as out_file:
        for line in clean_code:
            if line.startswith("@"):  # checks if a instruction
                if not line[1:].isdigit():  # if symbol
                    if line[1:] in symbol_dict.keys():  # if exists in dict
                        inst = symbol_dict[line[1:]]
                    else:  # not exists in dict
                        symbol_dict[line[1:]] = symbol_count
                        inst = symbol_count
                        symbol_count += 1
                else:
                    inst = line[1:]

                out_file.write(convert_a_inst(inst) + '\n')
            else:
                out_file.write(convert_c_inst(line) + '\n')


def translate_to_hack(file_name):
    """
    this method is responsible for translating one .asm file.
    """
    line_count = -1  # counting the valid code lines
    out_file_name = file_name
    out_file_name = out_file_name.replace(".asm", ".hack")
    with open(file_name, "r") as code:
        lines = code.readlines()

    clean_code = []  # contains the lines of the code without comments
    for line in lines:
        line = line.replace(" ", "")
        line = line.replace("\r","");
        if line.startswith("//") or line == '\n':  # skipping redundant lines
            continue
        comment_ind = line.find("/")
        line = line[:comment_ind]  # removing the comment
        if line.startswith("("):
            symbol_dict[line[1:-1]] = line_count + 1
        else:
            clean_code.append(line)
            line_count += 1

    write_to_out(clean_code, out_file_name)


if __name__ == "__main__":
    """
    this is the main method. responsible for receiving a path and translate 
    the given files to hack
    """
    first_arg = sys.argv[1]
    if os.path.isdir(first_arg):
        lst_files = os.listdir(first_arg)
        for file in lst_files:
            if file.endswith(".asm"):
                translate_to_hack(first_arg + "/" + file)
    if os.path.isfile(first_arg) and first_arg.endswith(".asm"):
        translate_to_hack(first_arg)
