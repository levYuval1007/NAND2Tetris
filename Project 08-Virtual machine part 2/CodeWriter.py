class CodeWriter:
    """
    this class is responsible for translating the given commands to asm,
    and write all translated commands to an output asm file.
    """
    label_tf_counter = 1  # counting true/false labels.
    label_xy_counter = 1  # counting check x and check y labels
    label_return_counter = 1  # counting the number of return labels
    cur_function = ""  # contains the name of the current function
    sys_init_flag = 1  # a flag which indicates if we need to write the
    # sys.init code or not.

    # all arithmetic commands translations
    arithmetic_line_dict1 = {"add": "D=D+M", "sub": "D=M-D", "or": "D=D|M",
                             "and": "D=D&M"}

    arithmetic_line_dict2 = {"neg": "M=-M", "not": "M=!M"}

    arithmetic_line_dict3 = {"gt": "D;JGT", "lt": "D;JLT", "eq": "D;JEQ"}

    ram_types_dict = {"local": "LCL", "argument": "ARG", "this": "THIS",
                      "that": "THAT"}

    ram_types_dict2 = {"temp": 5, "pointer": 3}

    def __init__(self, parsed_lines, out_file, cur_file_name):
        """
        initializing a new code writer object.
        :param parsed_lines: an array of all splitted code lines
        :param out_file: the output asm file (empty at the beginning)
        :param cur_file_name: the name of the current vm file we are
        translating
        """
        self.__parsed_lines = parsed_lines
        self.__cur_file_name = cur_file_name
        self.__out = out_file
        if CodeWriter.sys_init_flag:
            self.write_boot_strap()
            CodeWriter.sys_init_flag = 0
        self.write_lines()

    def write_arithmetic(self, arg1):
        """
        this method is responsible for writing all kinds of arithmetic commands
        :param arg1: the arithmetic command type
        """
        if arg1 in CodeWriter.arithmetic_line_dict1.keys():  # handling
            # "add", "sub", "and", "or"
            line = CodeWriter.arithmetic_line_dict1[arg1]
            self.__out.write("@SP\n")
            self.__out.write("M=M-1\n")
            self.__out.write("A=M\n")
            self.__out.write("D=M\n")
            self.__out.write("A=A-1\n")
            self.__out.write("%s\n" % (line,))
            self.__out.write("M=D\n")

        elif arg1 in CodeWriter.arithmetic_line_dict2.keys():  # handling
            # "neg", "not
            line = CodeWriter.arithmetic_line_dict2[arg1]
            self.__out.write("@SP\n")
            self.__out.write("M=M-1\n")
            self.__out.write("A=M\n")
            self.__out.write("%s\n" % (line,))
            self.__out.write("@SP\n")
            self.__out.write("M=M+1\n")

        else:  # handling "lt" "gt", "eq"
            # here we splitted to different functions in order to keep track
            #  of the line jumps
            self.__out.write("@SP\n")
            self.__out.write("M=M-1\n")
            if arg1 == "lt":
                self.write_lt()
            elif arg1 == "gt":
                self.write_gt()
            else:
                self.write_eq()

    def write_check_x_y_labels(self):
        """
        this method is writing the labels check x and check y when there is
        a call for lt/gt commands
        """
        self.__out.write(
            "(CHECK_Y_%s)  // checking if 2 numbers are signed the same\n" % (
                CodeWriter.label_xy_counter,))  # checking if 2 numbers are
        # signed the same
        self.__out.write("@R13\n")
        self.__out.write("M=0\n")
        self.__out.write("@SP\n")
        self.__out.write("A=M\n")
        self.__out.write("D=M\n")
        self.__out.write("@CHECK_X_%s\n" % (CodeWriter.label_xy_counter,))
        self.__out.write("D;JLT\n")
        self.__out.write("@2  // if y>0, add 2 to R13\n")
        self.__out.write("D=A\n")
        self.__out.write("@R13\n")
        self.__out.write("M=M+D\n")
        self.__out.write("(CHECK_X_%s)\n" % (CodeWriter.label_xy_counter,))
        self.__out.write("@SP\n")
        self.__out.write("M=M-1\n")
        self.__out.write("A=M\n")
        self.__out.write("D=M\n")
        self.__out.write(
            "@CONTINUE_AFTER_CHECK_XY_%s\n" % (CodeWriter.label_xy_counter,))
        self.__out.write("D;JLT\n")
        self.__out.write("@R13\n")
        self.__out.write("M=M+1  // if x>0, add 1 to R13\n")
        self.__out.write(
            "(CONTINUE_AFTER_CHECK_XY_%s)\n" % (CodeWriter.label_xy_counter,))
        CodeWriter.label_xy_counter += 1

    def write_false_true_labels(self):
        """
        this method is writing the labels insert true and insert false when
        there is a need for inserting a boolean value to the stack
        """
        self.__out.write("(INSERT_FALSE_%s)\n" % (
            CodeWriter.label_tf_counter,))  # insert false label
        self.__out.write("@SP  // insert false to the stack\n")
        self.__out.write("A=M\n")
        self.__out.write("M=0\n")
        self.__out.write("@SP\n")
        self.__out.write("M=M+1\n")
        self.__out.write(
            "@CONTINUE_AFTER_F_T_%s  // jump to the rest of the program\n" % (
                CodeWriter.label_tf_counter,))
        self.__out.write("0;JMP\n")
        self.__out.write("(INSERT_TRUE_%s)\n" % (
            CodeWriter.label_tf_counter,))  # insert true label
        self.__out.write("@SP  // insert true to the stack\n")
        self.__out.write("A=M\n")
        self.__out.write("M=-1\n")
        self.__out.write("@SP\n")
        self.__out.write("M=M+1\n")
        self.__out.write(
            "(CONTINUE_AFTER_F_T_%s)\n" % (CodeWriter.label_tf_counter,))
        CodeWriter.label_tf_counter += 1

    def write_eq(self):
        """
        handling eq command
        """
        self.__out.write("@SP\n")
        self.__out.write("A=M\n")
        self.__out.write("D=M\n")
        self.__out.write("@SP\n")
        self.__out.write("M=M-1\n")
        self.__out.write("A=M\n")
        self.__out.write(
            "D=D-M  // in order to check if the 2 numbers are equal\n")
        self.__out.write("@INSERT_TRUE_%s\n" % (
            CodeWriter.label_tf_counter,))  # two numbers are equal
        self.__out.write("D;JEQ\n")
        self.write_false_true_labels()

    def write_lt(self):
        """
        handling the lt command
        """
        self.write_check_x_y_labels()
        # checking the sign of x and y according to the result in R13 (0-
        # both negative, 1- x is positive and y is negative, 2- the opposite
        #  of 1, 3- both positive)
        self.__out.write("@2\n")
        self.__out.write("D=A\n")
        self.__out.write("@R13\n")
        self.__out.write("D=M-D\n")
        self.__out.write("@INSERT_TRUE_%s\n" % (CodeWriter.label_tf_counter,))
        self.__out.write("D;JEQ\n")
        self.__out.write("@R13\n")
        self.__out.write("D=M-1\n")
        self.__out.write("@INSERT_FALSE_%s\n" % (CodeWriter.label_tf_counter,))
        self.__out.write("D;JEQ\n")
        self.__out.write("@SP\n")
        self.__out.write("D=M\n")
        self.__out.write("A=D+1\n")
        self.__out.write("D=M\n")
        self.__out.write("@SP\n")
        self.__out.write("A=M\n")
        self.__out.write("D=M-D\n")
        self.__out.write("@INSERT_TRUE_%s\n" % (CodeWriter.label_tf_counter,))
        self.__out.write("D;JLT\n")
        self.write_false_true_labels()

    def write_gt(self):
        """
        handling gt command , same as lt
        """
        self.write_check_x_y_labels()
        self.__out.write("@2\n")
        self.__out.write("D=A\n")
        self.__out.write("@R13\n")
        self.__out.write("D=M-D\n")
        self.__out.write("@INSERT_FALSE_%s\n" % (CodeWriter.label_tf_counter,))
        self.__out.write("D;JEQ\n")
        self.__out.write("@R13\n")
        self.__out.write("D=M-1\n")
        self.__out.write("@INSERT_TRUE_%s\n" % (CodeWriter.label_tf_counter,))
        self.__out.write("D;JEQ\n")
        self.__out.write("@SP\n")
        self.__out.write("D=M\n")
        self.__out.write("A=D+1\n")
        self.__out.write("D=M\n")
        self.__out.write("@SP\n")
        self.__out.write("A=M\n")
        self.__out.write("D=M-D\n")
        self.__out.write("@INSERT_TRUE_%s\n" % (CodeWriter.label_tf_counter,))
        self.__out.write("D;JGT\n")
        self.write_false_true_labels()

    def write_push_pop(self, type, segment, index):
        """
        writing push/pop commands.
        :param type:  push / pop
        :param segment: variable type
        :param index: the variable location index
        """
        if segment == "constant":  # only push allowed
            self.__out.write("@%s\n" % (str(index),))
            self.__out.write("D=A\n")
            self.__out.write("@SP\n")
            self.__out.write("A=M\n")
            self.__out.write("M=D\n")
            self.__out.write("@SP\n")
            self.__out.write("M=M+1\n")
            return

        elif segment in CodeWriter.ram_types_dict.keys():  # variables
            # located in RAM1-RAM4: local, argument, this and that.
            self.__out.write("@%s\n" % (str(index),))
            self.__out.write("D=A\n")
            self.__out.write("@%s\n" % (self.ram_types_dict[segment],))
            self.__out.write("A=M\n")
            self.__out.write("D=A+D\n")

        elif segment in CodeWriter.ram_types_dict2.keys():  # temp, pointer
            self.__out.write(
                "@%s\n" % (self.ram_types_dict2[segment] + int(index),))
            self.__out.write("D=A\n")
        else:  # handling static
            self.__out.write("@%s.%s\n" % (self.__cur_file_name, index))
            self.__out.write("D=A\n")

        if type == "push":
            self.__out.write("A=D\n")
            self.__out.write("D=M\n")
            self.__out.write("@SP\n")
            self.__out.write("A=M\n")
            self.__out.write("M=D\n")
            self.__out.write("@SP\n")
            self.__out.write("M=M+1\n")

        if type == "pop":
            self.__out.write("@R14\n")
            self.__out.write("M=D\n")
            self.__out.write("@SP\n")
            self.__out.write("M=M-1\n")
            self.__out.write("A=M\n")
            self.__out.write("D=M\n")
            self.__out.write("@R14\n")
            self.__out.write("A=M\n")
            self.__out.write("M=D\n")

    def init_n_locals(self, n_vars):  # sp and lcl is located after "that".
        """
        this method is initializing all locals for the current function
        :param n_vars: number of local to init
        """
        for i in range(int(n_vars)):
            self.__out.write("@SP\n")
            self.__out.write("A=M\n")
            self.__out.write("M=0\n")
            self.__out.write("@SP\n")
            self.__out.write("M=M+1\n")

    def write_goto(self, line):
        """
        this method is writing a goto command
        :param line: the vm goto command
        """
        self.__out.write("@%s$%s\n" % (CodeWriter.cur_function, line[1]))
        self.__out.write("0;JMP\n")

    def write_if_goto(self, line):
        """
        this method is writing an if-goto command
        :param line: vm if-goto command
        """
        self.__out.write("@SP\n")
        self.__out.write("AM=M-1\n")
        self.__out.write("D=M\n")
        self.__out.write("@%s$%s\n" % (CodeWriter.cur_function, line[1]))
        self.__out.write("D;JNE\n")  # jump only if the last element is the
        # stack is not 0

    def write_label(self, line):
        """
        this method is writing a label command
        :param line: vm label command
        """
        self.__out.write("(%s$%s)\n" % (CodeWriter.cur_function, line[1]))

    def write_function(self, line):
        """
        this method is writing a function declaration
        :param line: the vm function declaration
        """
        self.__out.write("(%s)\n" % (line[1],))
        self.init_n_locals(line[2])
        CodeWriter.cur_function = line[1]

    def write_return(self):
        """
        this method is writing a return command.
        """
        self.__out.write("@5\n")
        self.__out.write("D=A\n")
        self.__out.write("@LCL\n")
        self.__out.write("AD=M-D\n")
        self.__out.write("D=M\n")
        self.__out.write("@R13\n")
        self.__out.write("M=D\n")
        self.__out.write("@SP  // updating return value\n")
        self.__out.write("A=M-1\n")
        self.__out.write("D=M\n")
        self.__out.write("@ARG\n")
        self.__out.write("A=M\n")
        self.__out.write("M=D\n")
        self.__out.write("@ARG\n")
        self.__out.write("D=M\n")
        self.__out.write("@SP  // updating saved addresses\n")
        self.__out.write("M=D+1\n")
        self.__out.write("@LCL\n")
        self.__out.write("D=M\n")
        self.__out.write("@R15\n")
        self.__out.write("AM=D-1\n")
        self.__out.write("D=M\n")
        self.__out.write("@THAT\n")
        self.__out.write("M=D\n")
        self.__out.write("@R15\n")
        self.__out.write("AM=M-1\n")
        self.__out.write("D=M\n")
        self.__out.write("@THIS\n")
        self.__out.write("M=D\n")
        self.__out.write("@R15\n")
        self.__out.write("AM=M-1\n")
        self.__out.write("D=M\n")
        self.__out.write("@ARG\n")
        self.__out.write("M=D\n")
        self.__out.write("@R15\n")
        self.__out.write("AM=M-1\n")
        self.__out.write("D=M\n")
        self.__out.write("@LCL\n")
        self.__out.write("M=D\n")
        self.__out.write("@R13\n")
        self.__out.write("A=M\n")
        self.__out.write("0;JMP  // jumping back to the caller\n")

    def write_call(self, line):
        """
        this method is writing a call command
        :param line: the vm call command
        :return:
        """
        self.__out.write("@%s$ret.%s  // saving all necessary fields\n" % (
            CodeWriter.cur_function,
            CodeWriter.label_return_counter))
        self.__out.write("D=A\n")
        self.insert_value_to_sp()
        self.__out.write("@LCL\n")
        self.__out.write("D=M\n")
        self.insert_value_to_sp()
        self.__out.write("@ARG\n")
        self.__out.write("D=M\n")
        self.insert_value_to_sp()
        self.__out.write("@THIS\n")
        self.__out.write("D=M\n")
        self.insert_value_to_sp()
        self.__out.write("@THAT\n")
        self.__out.write("D=M\n")
        self.insert_value_to_sp()
        self.__out.write("@SP\n")
        self.__out.write("D=M\n")
        self.__out.write("@LCL\n")
        self.__out.write("M=D\n")
        self.__out.write("@%s\n" % (5 + int(line[2]),))  # saved fields +
        # num of arguments
        self.__out.write("D=A\n")
        self.__out.write("@SP\n")
        self.__out.write("D=M-D\n")
        self.__out.write("@ARG\n")
        self.__out.write("M=D\n")
        self.__out.write("@%s // jumping to callee\n" % (line[1],))
        self.__out.write("0;JMP\n")
        self.__out.write("(%s$ret.%s)  //continuing program \n" % (
            CodeWriter.cur_function,
            CodeWriter.label_return_counter))
        CodeWriter.label_return_counter += 1

    def insert_value_to_sp(self):
        """
        this method is responsible for writing the asm code required for
        advancing the sp.
        """
        self.__out.write("@SP\n")
        self.__out.write("A=M\n")
        self.__out.write("M=D\n")
        self.__out.write("@SP\n")
        self.__out.write("M=M+1\n")

    def write_boot_strap(self):
        """
        this function is calling the function sys.init
        """
        self.__out.write("@256\n")
        self.__out.write("D=A\n")
        self.__out.write("@SP\n")
        self.__out.write("M=D\n")
        self.write_call(["call", "Sys.init", "0"])

    def write_lines(self):
        """
        going through all parsed lines and translate each line to asm code.
        """
        for line in self.__parsed_lines:
            str_line = "// " + line[0] + " " + str(line[1]) + " " + \
                       str(line[2]) + "\n"
            self.__out.write(str_line)
            if line[0] == "push" or line[0] == "pop":
                self.write_push_pop(line[0], line[1], line[2])
            elif line[0] == "label":
                self.write_label(line)
            elif line[0] == "goto":
                self.write_goto(line)
            elif line[0] == "if-goto":
                self.write_if_goto(line)
            elif line[0] == "function":
                self.write_function(line)
            elif line[0] == "call":
                self.write_call(line)
            elif line[0] == "return":
                self.write_return()
            else:
                self.write_arithmetic(line[0])
