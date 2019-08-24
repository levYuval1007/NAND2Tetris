"""
this class is responsible for writing vm code to output file
"""


class VMWriter:

    def __init__(self, out_file):
        """
        init new vm writer object
        :param out_file
        """
        self.__file = out_file

    def write_label(self, label):
        """
        write label
        :param label: label name
        """
        self.__file.write("label " + label + "\n")

    def write_go_to(self, label):
        """
        write go to
        :param label: label name
        """
        self.__file.write("goto " + label + "\n")

    def write_if(self, label):
        """
        write if go to
        :param label: label name
        """
        self.__file.write("if-goto " + label + "\n")

    def write_call(self, func_name, arg_num):
        """
        write call to func
        :param func_name: func name
        :param arg_num: num of args
        """
        self.__file.write("call " + func_name + " " + str(arg_num) + "\n")

    def write_function(self, name, locals):
        """
        write declaration of function
        :param name: func name
        :param locals: num of locals
        """
        self.__file.write("function " + name + " " + str(locals) + "\n")

    def write_arithmetic(self, command):
        """
        write arithmetic command
        :param command: arithmetic command
        """
        self.__file.write(command + "\n")

    def write_return(self):
        """
        write return
        """
        self.__file.write("return\n")

    def write_push(self, segment, ind):
        """
        write push command
        :param segment: var kind
        :param ind: var index
        """
        if segment == "field":
            segment = "this"
        self.__file.write("push " + segment + " " + str(ind) + "\n")

    def write_pop(self, segment, ind):
        """
        write pop command
        :param segment: var kind
        :param ind: var index
        """
        self.__file.write("pop " + segment + " " + str(ind) + "\n")

    def push_val(self, val):
        """
        write push according to val data
        :param val: the val data
        """
        kind = val[1]
        if val[1] == "field":
            kind = "this"
        self.write_push(kind, val[2])

    def close(self):
        """
        closes the file
        """
        self.__file.close()
