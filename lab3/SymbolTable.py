class Symbol(object):
    pass


class VariableSymbol(Symbol):
    def __init__(self, name, type, lineno):
        self.name = name
        self.type = type
        self.lineno = lineno


class FunctionSymbol(Symbol):
    def __init__(self, name, type, table, lineno):
        self.name = name
        self.type = type
        self.args = []
        self.table = table
        self.lineno = lineno

    def extract_args(self):
        self.args = [x for x in self.table.symbols.values()]


class DuplicationError(RuntimeError):
    def __init__(self, name, symbol_table_name):
        self.name = name
        self.symbol_table_name = symbol_table_name

    def __str__(self):
        return "Duplicated name: " + self.name + " in symbol table: " + self.symbol_table_name


class SymbolTable(object):
    def __init__(self, parent, name):  # parent scope and symbol table name
        self.symbols = {}
        self.parent = parent
        self.name = name
        pass

    def put(self, name, symbol):  # put variable symbol or fundef under <name> entry
        try:
            _ = self.symbols[name]
            raise DuplicationError(name, self.name)
        except KeyError:
            self.symbols[name] = symbol

    def get(self, name):  # get variable symbol or fundef from <name> entry
        try:
            s = self.symbols[name]
            return s
        except KeyError:
            return None

    def getGlobal(self, name):
        s = self.get(name)
        if s is None:
            if self.parent is not None:
                return self.parent.getGlobal(name)
            else:
                return None
        else:
            return s

    def getParentScope(self):
        return self.parent