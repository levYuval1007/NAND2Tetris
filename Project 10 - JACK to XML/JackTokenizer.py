"""
this class is responsible for tokenizing a single jack code file. The class is creating a list with all tokens.
"""


class JackTokenizer:

    KEYWORD = "keyword"
    SYMBOL = "symbol"
    INT_CONST = "integerConstant"
    STR_CONST = "stringConstant"
    IDENTIFIER = "identifier"

    keywords = {"class", "constructor", "function", "method", "field",
                "static", "var", "int", "char", "boolean", "void", "true",
                "false", "null", "this", "let", "do", "if", "else", "while",
                "return"}

    symbols = "{}[]().,;+-*/&|><=~"

    redundant = {"\n", "\r", "\t", " "}

    def __init__(self, file):
        """
        initializing a new tokenizer object.
        :param file: a jack code file
        """
        self.__in_file = file
        self.__token = ""  # will contain the current token
        self.__tokens = []  # will contain all tokens
        self.__lines = file.readlines()
        self.__lines = "".join(self.__lines)  # all lines as one string, in order to make the iteration easier.
        self.__i = 0
        self.build_tokens()

    def build_tokens(self):
        """
        creating the tokens list
        """
        self.advance()
        while self.__token != "":
            self.__tokens.append(self.token_type())
            self.advance()

    def token_type(self):
        """
        :return: a tuple containing the token and its type
        """
        self.__token = self.__token.strip("\t\n\r")

        if self.__token in JackTokenizer.keywords:
            if self.__token == "this" and (self.__tokens[-1])[1] == "let":  # in case "this" comes after let
                return JackTokenizer.IDENTIFIER, self.__token

            return JackTokenizer.KEYWORD, self.__token

        elif JackTokenizer.symbols.find(self.__token) != -1:
            if self.__token == "<":
                self.__token = "&lt;"
            elif self.__token == ">":
                self.__token = "&gt;"
            elif self.__token == "&":
                self.__token = "&amp;"
            return JackTokenizer.SYMBOL, self.__token

        elif self.__token[0] == "\"" and self.__token[-1] == "\"":
            return JackTokenizer.STR_CONST, self.__token[1:-1].strip()

        elif self.__token.isdigit():
            return JackTokenizer.INT_CONST, self.__token

        else:
            return JackTokenizer.IDENTIFIER, self.__token

    def advance(self):
        """
        going over the code and collecting tokens by reading chars.
        """
        self.__token = ""
        if self.__i >= len(self.__lines):
            return
        while self.__i < len(self.__lines) and self.__lines[self.__i] in JackTokenizer.redundant:  # advance as long as you see redundant chars
            self.__i += 1

        if self.__i >= len(self.__lines):
            return

        if self.__lines[self.__i] == "\"":
            self.update()
            while self.__lines[self.__i] != "\"":  # str const
                self.update()
            self.update()
            return

        if self.__lines[self.__i].isdigit():  # int const
            while self.__lines[self.__i].isdigit():
                self.update()
            return

        if self.__i < (len(self.__lines) - 1) and self.__lines[self.__i:self.__i + 2] == "//":  # comment
            while self.__i < len(self.__lines) and self.__lines[self.__i] != "\n":
                self.__i += 1
            self.advance()
            return

        if self.__i < (len(self.__lines) - 1) and self.__lines[self.__i:self.__i + 2] == "/*":  # comment
            self.__i += 1
            while self.__lines[self.__i:self.__i + 2] != "*/":
                self.__i += 1
            self.__i += 2
            self.advance()
            return

        if self.__i < (len(self.__lines) - 2) and self.__lines[self.__i:self.__i + 3] == "/**":  # comment
            self.__i += 2
            while self.__lines[self.__i:self.__i + 2] != "*/":
                self.__i += 1
            self.__i += 2
            self.advance()
            return

        if self.__lines[self.__i] in JackTokenizer.symbols:  # symbol
            self.update()
            return

        else:  # other cases
            while self.__lines[self.__i] not in JackTokenizer.symbols and self.__lines[self.__i] not in " \t\r\n":
                self.update()

    def update(self):
        """
        adding the current char to the token and progressing i which now "points" to the next char in the text
        """
        self.__token += self.__lines[self.__i]
        self.__i += 1

    def get_tokens(self):
        """
        :return: the tokens array
        """
        return self.__tokens
