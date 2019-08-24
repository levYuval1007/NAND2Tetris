import sys
import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def handle_file(file_name):
    """
    this function is handling a single jack file
    :param file_name:
    :return:
    """
    with open(file_name, "r") as file:
        tokenizer = JackTokenizer(file)
        file_name = file_name.replace(".jack", ".xml")
    with open(file_name, "w") as out_file:
        CompilationEngine(tokenizer.get_tokens(), out_file)


if __name__ == "__main__":
    """
    this is the main method. responsible for receiving a path and translate 
    the given files to xml
    """
    first_arg = sys.argv[1]
    if os.path.isdir(first_arg):
        lst_files = os.listdir(first_arg)
        for file in lst_files:
            if file.endswith(".jack"):
                handle_file(first_arg + "/" + file)
    if os.path.isfile(first_arg) and first_arg.endswith(".jack"):
        handle_file(first_arg)
