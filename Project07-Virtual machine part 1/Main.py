import sys
from Parser import Parser
from CodeWriter import CodeWriter
import os

if __name__ == "__main__":
    """
    this is the main method, responsible for collecting the vm files and 
    construct the relevant objects in order to translate the files to asm
    """
    first_arg = sys.argv[1]
    file_name = os.path.basename(first_arg)
    if os.path.isdir(first_arg):  # when given path is a directory
        path = first_arg + "/" + file_name + ".asm"
        lst_files = os.listdir(first_arg)
        with open(path, "a") as asm_file:
            for file in lst_files:
                if file.endswith(".vm"):
                    cur_name = file.replace(".vm", "")
                    parser = Parser(first_arg + "/" + file)
                    parsed_lines = parser.get_parsed_lines()
                    code_writer = CodeWriter(parsed_lines, asm_file, cur_name)

    if os.path.isfile(first_arg) and first_arg.endswith(".vm"):  # when
        # given path is a single file
        path = first_arg.replace(".vm", ".asm")
        with open(path, "a") as asm_file:
            parser = Parser(first_arg)
            parsed_lines = parser.get_parsed_lines()
            code_writer = CodeWriter(parsed_lines, asm_file, file_name[:-3])
