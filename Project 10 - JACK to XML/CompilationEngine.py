from JackTokenizer import JackTokenizer

"""
this class is responsible for writing the output xml file, by compiling all syntax cases possible in jack
"""


class CompilationEngine:

    all_operators = {"+", "-", "/", "*", "&amp;", "|", "&gt;", "&lt;", "="}

    def __init__(self, tokens, out_file):
        """
        initializing a new compile engine object
        :param tokens: the list of tokens created by the tokenizer
        :param out_file: the output file.
        """
        self.__tokens = tokens
        self.__file = out_file
        self.__i = 0
        self.compile_class()

    def eat(self):
        """
        compiling a single token and move to the next one
        """
        tup = self.__tokens[self.__i]
        self.__file.write("<" + tup[0] + ">" + " " + tup[1] + " " + "</" + tup[0] + ">\n")
        self.__i += 1

    def peek(self):
        """
        checking the current token without compiling
        :return: the token
        """
        ret_val = self.__tokens[self.__i]
        return ret_val[1]

    def peek_type(self):
        """
        checking the current token type without compiling
        :return: the token type
        """
        ret_val = self.__tokens[self.__i]
        return ret_val[0]

    def peek_ll2(self):
        """
        checking two tokens ahead without compiling
        :return: the token
        """
        ret_val = self.__tokens[self.__i + 1]
        return ret_val[1]

    def compile_while_stat(self):  # i points to while
        """
        compiling while statement
        """
        self.__file.write("<whileStatement>\n")
        self.eat()
        self.eat()
        self.compile_expression()
        self.eat()
        self.eat()
        self.compile_statements()
        self.eat()
        self.__file.write("</whileStatement>\n")

    def compile_return_stat(self):  # i points to return
        """
        compiling return statement
        """
        self.__file.write("<returnStatement>\n")
        self.eat()
        if not self.peek() == ";":
            self.compile_expression()
        self.eat()
        self.__file.write("</returnStatement>\n")

    def compile_do_stat(self):
        """
        compiling do statement
        """
        self.__file.write("<doStatement>\n")
        self.eat()
        self.compile_subroutine_call()
        self.eat()
        self.__file.write("</doStatement>\n")

    def compile_if_stat(self):
        """
        compiling if statement
        """
        self.__file.write("<ifStatement>\n")
        self.eat()
        self.eat()
        self.compile_expression()
        self.eat()
        self.eat()
        self.compile_statements()
        self.eat()
        if self.peek() == "else":
            self.eat()
            self.eat()
            self.compile_statements()
            self.eat()
        self.__file.write("</ifStatement>\n")

    def compile_class_var_dec(self):
        """
        compiling class variable declaration
        """
        self.__file.write("<classVarDec>\n")
        self.eat()
        self.var_dec_helper()
        self.__file.write("</classVarDec>\n")

    def compile_var_dec(self):
        """
        compiling variable declaration
        """
        self.__file.write("<varDec>\n")
        self.eat()
        self.var_dec_helper()
        self.__file.write("</varDec>\n")

    def var_dec_helper(self):

        self.eat()
        self.eat()
        cur_stat = self.peek()
        while cur_stat != ";":
            self.eat()
            self.eat()
            cur_stat = self.peek()
        self.eat()

    def compile_subroutine_body(self):
        """
        compiling subroutine body
        """
        self.__file.write("<subroutineBody>\n")
        self.eat()
        cur_stat = self.peek()
        while cur_stat == "var":
            self.compile_var_dec()
            cur_stat = self.peek()
        self.compile_statements()
        self.eat()
        self.__file.write("</subroutineBody>\n")

    def compile_parameter_list(self):
        """
        compiling parameters list
        """
        self.__file.write("<parameterList>\n")
        cur_stat = self.peek()
        if cur_stat != ")":
            self.eat()
            self.eat()
            cur_stat = self.peek()

        while cur_stat == ",":
            self.eat()
            self.eat()
            self.eat()
            cur_stat = self.peek()

        self.__file.write("</parameterList>\n")

    def compile_class(self):
        """
        compiling class
        """
        self.__file.write("<class>\n")
        self.eat()
        self.eat()
        self.eat()
        cur_stat = self.peek()

        while cur_stat == "static" or cur_stat == "field":
            self.compile_class_var_dec()
            cur_stat = self.peek()

        while cur_stat != "}":
            self.compile_subroutine_dec()
            cur_stat = self.peek()
        self.eat()
        self.__file.write("</class>\n")

    def compile_expression(self):
        """
        compiling expression
        """
        self.__file.write("<expression>\n")
        self.compile_term()
        cur_stat = self.peek()
        while cur_stat in CompilationEngine.all_operators:
            self.eat()
            self.compile_term()
            cur_stat = self.peek()
        self.__file.write("</expression>\n")

    def compile_statements(self):
        """
        compiling statements
        """
        self.__file.write("<statements>\n")
        while self.compile_statement():
            continue
        self.__file.write("</statements>\n")

    def compile_subroutine_call(self):
        """
        compiling subroutine call
        """
        self.eat()
        cur_stat = self.peek()
        if cur_stat == "(":
            self.eat()
            self.compile_expression_list()
            self.eat()
        else:
            self.eat()
            self.eat()
            self.eat()
            self.compile_expression_list()
            self.eat()

    def compile_expression_list(self):
        """
        compiling expression list
        """
        self.__file.write("<expressionList>\n")
        cur_stat = self.peek()
        if cur_stat != ")":
            self.compile_expression()
            cur_stat = self.peek()

        while cur_stat == ",":
            self.eat()
            self.compile_expression()
            cur_stat = self.peek()
        self.__file.write("</expressionList>\n")

    def compile_statement(self):
        """
        compiling statement
        """
        cur_stat = self.peek()
        if cur_stat == "if":
            self.compile_if_stat()
        elif cur_stat == "while":
            self.compile_while_stat()
        elif cur_stat == "do":
            self.compile_do_stat()
        elif cur_stat == "return":
            self.compile_return_stat()
        elif cur_stat == "let":
            self.compile_let_stat()
        else:
            return 0  # when there is no more statements to compile
        return 1

    def compile_let_stat(self):
        """
        compiling let statement
        """
        self.__file.write("<letStatement>\n")
        self.eat()
        self.eat()
        cur_stat = self.peek()
        if cur_stat == "[":
            self.eat()
            self.compile_expression()
            self.eat()
        self.eat()
        self.compile_expression()
        self.eat()
        self.__file.write("</letStatement>\n")

    def compile_subroutine_dec(self):
        """
        compiling subroutine declaration
        """
        self.__file.write("<subroutineDec>\n")
        self.eat()
        self.eat()
        self.eat()
        self.eat()
        self.compile_parameter_list()
        self.eat()
        self.compile_subroutine_body()
        self.__file.write("</subroutineDec>\n")

    def compile_term(self):
        """
        compiling term
        """
        self.__file.write("<term>\n")
        cur_stat = self.peek_type()
        if cur_stat == JackTokenizer.KEYWORD or cur_stat == \
                JackTokenizer.INT_CONST or cur_stat == JackTokenizer.STR_CONST:
            self.eat()
            self.__file.write("</term>\n")
            return
        cur_stat = self.peek()
        if cur_stat == "(":
            self.eat()
            self.compile_expression()
            self.eat()
            self.__file.write("</term>\n")
            return
        if cur_stat == "-" or cur_stat == "~":
            self.eat()
            self.compile_term()
            self.__file.write("</term>\n")
            return
        cur_stat = self.peek_ll2()
        if cur_stat == "[":
            self.eat()
            self.eat()
            self.compile_expression()
            self.eat()
            self.__file.write("</term>\n")
            return
        if cur_stat == "." or cur_stat == "(":
            self.compile_subroutine_call()
            self.__file.write("</term>\n")
            return
        self.eat()
        self.__file.write("</term>\n")
        return
