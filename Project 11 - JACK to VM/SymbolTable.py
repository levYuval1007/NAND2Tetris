"""
this class is responsible for creating a symbol table for a class/subroutine
"""


class SymbolTable:

    # variable kinds
    STATIC = "static"
    FIELD = "field"
    ARG = "argument"
    VAR = "local"

    def __init__(self):
        """
        init new symbol table object
        """
        self.__table = {}
        self.__counters = {"static": 0, "local": 0, "field": 0, "argument": 0,
                           "pointer": 0}

    def add(self, name, type, kind):
        """
        adding a new variable to the table
        :param name: var name
        :param type: var type
        :param kind: var kind
        """
        self.__table[name] = (type, kind, self.__counters[kind])
        self.__counters[kind] += 1

    def get_data(self, name):
        """
        :param name: variable name
        :return: the data of the variable if found in table, false otherwise
        """
        if name in self.__table.keys():
            return self.__table[name]
        else:
            return False

    def var_count(self, kind):
        """
        :param kind: the kind to count
        :return: the current number of appearances of that kind
        """
        return self.__counters[kind]
