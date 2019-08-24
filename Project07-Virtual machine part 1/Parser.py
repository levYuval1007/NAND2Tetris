class Parser:
    """
    this class is responsible for parsing a given code file and split all
    lines to its components.
    """

    def __init__(self, vm_file_path):
        """
        initializing a new parser object
        :param vm_file_path: the path for the current code file
        """
        self.__file_name = vm_file_path  # the vm code file path
        with open(vm_file_path, "r") as file:
            self.__file = file
            self.__cur_line = ""
            self.__cur_line_arr = []  # contains the current splitted line
            self.__parsed_lines = []  # contains all splitted code lines

            self.process_commands()

    def process_commands(self):
        """
        this method is responsible for remove redundant white spaces and
        calling other functions to split the code lines
        """
        self.advance()
        while self.has_more_commands():

            if self.__cur_line.startswith("//") or self.__cur_line == '\n':
                self.advance()
                # skipping redundant lines
                continue
            self.__cur_line = self.__cur_line.replace("\n", "") #maybe remove
            comment_ind = self.__cur_line.find("//")
            if comment_ind != -1:
                self.__cur_line = self.__cur_line[:comment_ind]  # removing the
            # comment
            self.parse_command_line()
            self.advance()

    def has_more_commands(self):
        """
        :return: false if there is no more line codes, and true otherwise.
        """
        return self.__cur_line != ""

    def advance(self):
        """
        reading the next code line from the file
        """
        self.__cur_line = self.__file.readline()
        self.__cur_line = self.__cur_line.replace("\t", " ")
        self.__cur_line = self.__cur_line.replace("\r", " ")
        self.__cur_line = self.__cur_line.strip(" ")

    def parse_command_line(self):
        """
        this method is taking a single code line and split it to its
        components. The first cell in the command array is the command type, the
        second is the variable type or the arithmetic command type, and the
        third is the index
        """
        line = [-1] * 3  # initializing the current command array
        j = 0
        self.__cur_line_arr = self.__cur_line.split(" ")
        for i in range(len(self.__cur_line_arr)):
            if self.__cur_line_arr[i] == '':  # getting rid of redundant spaces
                continue
            line[j] = self.__cur_line_arr[i]
            j += 1

        self.__parsed_lines.append(line)

    def get_parsed_lines(self):
        """
        :return: the whole code splitted to small arrays, when every single
        array is a splitted code line.
        """
        return self.__parsed_lines
