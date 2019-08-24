from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

"""
this class is responsible for writing the output xml file, by compiling all 
syntax cases possible in jack
"""


class CompilationEngine:
    all_operators = {"+": "add", "-": "sub", "/": "div", "*": "mul",
                     "&amp;": "and", "|": "or", "&gt;": "gt", "&lt;": "lt",
                     "=": "eq"}

    def __init__(self, tokens, out_file):
        """
        initializing a new compile engine object
        :param tokens: the list of tokens created by the tokenizer
        :param out_file: the output file.
        """
        self.__tokens = tokens
        self.__file = out_file
        self.__i = 0
        self.__class_symbol = SymbolTable()
        self.__subroutine_symbol = SymbolTable()
        self.__cur_token = ()
        self.__class_name = ""
        self.__writer = VMWriter(out_file)
        self.__label_count = 0
        self.compile_class()
        self.__writer.close()

    def eat(self):
        """
        compiling a single token and move to the next one
        """
        self.__cur_token = self.__tokens[self.__i]
        self.__i += 1

    def get_token(self):
        return self.__cur_token[1]

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
        self.eat()
        self.eat()
        label_true = "L%s" % self.__label_count
        self.__label_count += 1
        label_continue = "L%s" % self.__label_count
        self.__label_count += 1
        self.__writer.write_label(label_true)
        self.compile_expression()
        self.__writer.write_arithmetic("not")
        self.__writer.write_if(label_continue)
        self.eat()
        self.eat()
        self.compile_statements()
        self.__writer.write_go_to(label_true)
        self.eat()
        self.__writer.write_label(label_continue)

    def compile_return_stat(self):  # i points to return
        """
        compiling return statement
        """
        self.eat()
        if not self.peek() == ";":
            self.compile_expression()
        else:
            self.__writer.write_push("constant", 0)
        self.__writer.write_return()
        self.eat()

    def compile_do_stat(self):
        """
        compiling do statement
        """
        self.eat()
        self.compile_subroutine_call()
        self.__writer.write_pop("temp", 0)
        self.eat()

    def compile_if_stat(self):
        """
        compiling if statement
        """
        self.eat()
        self.eat()
        self.compile_expression()
        self.__writer.write_arithmetic("not")
        label_false = "L%s" % self.__label_count
        self.__label_count += 1
        label_continue = "L%s" % self.__label_count
        self.__label_count += 1
        self.__writer.write_if(label_false)
        self.eat()
        self.eat()
        self.compile_statements()
        self.__writer.write_go_to(label_continue)
        self.eat()
        self.__writer.write_label(label_false)
        if self.peek() == "else":
            self.eat()
            self.eat()
            self.compile_statements()
            self.eat()
        self.__writer.write_label(label_continue)

    def compile_class_var_dec(self):
        """
        compiling class variable declaration
        """
        self.eat()
        kind = self.get_token()
        if kind == "var":
            kind = SymbolTable.VAR
        self.var_dec_helper(kind, self.__class_symbol)

    def compile_var_dec(self):
        """
        compiling variable declaration
        """
        self.eat()
        self.var_dec_helper(SymbolTable.VAR, self.__subroutine_symbol)

    def var_dec_helper(self, kind, symbol_table):

        self.eat()
        type = self.get_token()
        self.eat()
        name = self.get_token()
        symbol_table.add(name, type, kind)
        cur_stat = self.peek()
        while cur_stat != ";":
            self.eat()
            self.eat()
            name = self.get_token()
            symbol_table.add(name, type, kind)
            cur_stat = self.peek()
        self.eat()

    def compile_subroutine_body(self, func_name, func_type):
        """
        compiling subroutine body
        """
        self.eat()
        cur_stat = self.peek()
        while cur_stat == "var":
            self.compile_var_dec()
            cur_stat = self.peek()
        self.__writer.write_function(func_name,
                                     self.__subroutine_symbol.var_count(
                                         SymbolTable.VAR))
        self.__subroutine_symbol.add("this", self.__class_name, "pointer")
        if func_type == "method":
            self.__writer.write_push(SymbolTable.ARG, 0)
            self.__writer.write_pop("pointer", 0)

        elif func_type == "constructor":
            self.__writer.write_push("constant", self.__class_symbol.var_count(
                                         SymbolTable.FIELD))
            self.__writer.write_call("Memory.alloc", 1)
            self.__writer.write_pop("pointer", 0)
        self.compile_statements()
        self.eat()

    def compile_parameter_list(self):
        """
        compiling parameters list
        """
        cur_stat = self.peek()
        if cur_stat != ")":
            self.eat()
            type = self.get_token()
            self.eat()
            name = self.get_token()
            self.__subroutine_symbol.add(name, type, SymbolTable.ARG)
            cur_stat = self.peek()

        while cur_stat == ",":
            self.eat()
            self.eat()
            type = self.get_token()
            self.eat()
            name = self.get_token()
            self.__subroutine_symbol.add(name, type, SymbolTable.ARG)
            cur_stat = self.peek()

    def compile_class(self):
        """
        compiling class
        """
        self.eat()
        self.eat()
        self.__class_name = self.get_token()
        self.eat()
        cur_stat = self.peek()

        while cur_stat == "static" or cur_stat == "field":
            self.compile_class_var_dec()
            cur_stat = self.peek()

        while cur_stat != "}":
            self.compile_subroutine_dec()
            cur_stat = self.peek()
        self.eat()

    def compile_expression(self):
        """
        compiling expression
        """
        self.compile_term()
        cur_stat = self.peek()
        while cur_stat in CompilationEngine.all_operators.keys():
            self.eat()
            self.compile_term()
            self.compile_operation(cur_stat)
            cur_stat = self.peek()

    def compile_operation(self, op):
        """
        compiling operation
        :param op: current op
        """
        if op == "*":
            self.__writer.write_call("Math.multiply", 2)

        elif op == "/":
            self.__writer.write_call("Math.divide", 2)

        else:
            self.__writer.write_arithmetic(CompilationEngine.all_operators[op])

    def compile_statements(self):
        """
        compiling statements
        """
        while self.compile_statement():
            continue

    def compile_subroutine_call(self):
        """
        compiling subroutine call
        """
        self.eat()
        name = self.get_token()
        cur_stat = self.peek()
        if cur_stat == "(":
            self.eat()
            self.__writer.write_push("pointer", 0)
            args = self.compile_expression_list()
            self.eat()
            self.__writer.write_call(self.__class_name + "." + name, args + 1)
        else:
            self.eat()
            val = self.find(name)
            self.eat()
            var_name = self.get_token()
            self.eat()
            if not val:
                args = 0
            else:
                self.__writer.push_val(val)
                name = val[0]
                args = 1

            args += self.compile_expression_list()
            self.__writer.write_call(name + "." + var_name, args)
            self.eat()

    def compile_expression_list(self):
        """
        compiling expression list
        """
        args = 0
        cur_stat = self.peek()
        if cur_stat != ")":
            self.compile_expression()
            args += 1
            cur_stat = self.peek()

        while cur_stat == ",":
            self.eat()
            args += 1
            self.compile_expression()
            cur_stat = self.peek()

        return args

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
        self.eat()
        self.eat()
        name = self.get_token()
        data = self.find(name)
        kind = data[1]
        ind = data[2]

        if kind == "field":
            kind = "this"

        cur_stat = self.peek()
        if cur_stat == "[":
            self.compile_array(kind, ind)
        else:
            self.eat()
            self.compile_expression()
            self.__writer.write_pop(kind, ind)
        self.eat()  # eat ;

    def compile_subroutine_dec(self):
        """
        compiling subroutine declaration
        """
        self.eat()
        func_type = self.get_token()
        self.eat()
        self.eat()
        func_name = self.__class_name + "." + self.get_token()
        self.eat()
        if func_type == "method":
            self.__subroutine_symbol.add("this", self.__class_name,
                                         SymbolTable.ARG)
        self.compile_parameter_list()
        self.eat()
        self.compile_subroutine_body(func_name, func_type)
        self.__subroutine_symbol = SymbolTable()

    def compile_term(self):
        """
        compiling term
        """
        cur_stat = self.peek_type()
        if cur_stat == JackTokenizer.INT_CONST:
            self.__writer.write_push("constant", self.peek())
            self.eat()
            return

        if cur_stat == JackTokenizer.KEYWORD:
            if self.peek() == "null" or self.peek() == "false":
                self.__writer.write_push("constant", 0)

            elif self.peek() == "true":
                self.__writer.write_push("constant", 0)
                self.__writer.write_arithmetic("not")

            elif self.peek() == "this":
                self.__writer.write_push("pointer", 0)

            self.eat()
            return

        if cur_stat == JackTokenizer.STR_CONST:
            string1 = self.peek().replace('\t', "\\t")
            string2 = string1.replace('\n', "\\n")
            string3 = string2.replace('\r', "\\r")
            string = string3.replace('\b', "\\b")
            self.__writer.write_push("constant", len(string))
            self.__writer.write_call("String.new", 1)
            for ch in string:
                self.__writer.write_push("constant", ord(ch))
                self.__writer.write_call("String.appendChar", 2)
            self.eat()
            return

        cur_stat = self.peek()
        if cur_stat == "(":
            self.eat()
            self.compile_expression()
            self.eat()
            return

        if cur_stat == "-":
            self.eat()
            self.compile_term()
            self.__writer.write_arithmetic("neg")
            return

        if cur_stat == "~":
            self.eat()
            self.compile_term()
            self.__writer.write_arithmetic("not")
            return

        cur_stat = self.peek_ll2()
        if cur_stat == "[":
            self.eat()
            name = self.get_token()
            self.__writer.push_val(self.find(name))
            self.eat()
            self.compile_expression()
            self.__writer.write_arithmetic("add")
            self.__writer.write_pop("pointer", 1)
            self.__writer.write_push("that", 0)
            self.eat()
            return

        if cur_stat == "." or cur_stat == "(":
            self.compile_subroutine_call()
            return

        self.eat()  # varName
        name = self.get_token()
        self.__writer.push_val(self.find(name))
        return

    def find(self, name):
        """
        finding a variable name in symbol tables
        """
        val = self.__subroutine_symbol.get_data(name)
        if not val:
            val = self.__class_symbol.get_data(name)
        elif not val:
            return False
        return val

    def compile_array(self, kind, index):
        """
        compiling array assignment
        :param kind: var kind
        :param index: var index
        """
        self.eat()
        self.compile_expression()
        self.eat()
        self.__writer.write_push(kind, index)
        self.__writer.write_arithmetic("add")
        self.eat()
        self.compile_expression()
        self.__writer.write_pop("temp", 0)
        self.__writer.write_pop("pointer", 1)
        self.__writer.write_push("temp", 0)
        self.__writer.write_pop("that", 0)
