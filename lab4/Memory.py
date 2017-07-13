class Symbol(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Memory:
    def __init__(self, name):  # memory name
        self.name = name
        self.symbols = []

    def has_key(self, name):  # variable name
        for symbol in self.symbols:
            if symbol.name == name:
                return True
        return False

    def get(self, name):  # get from memory current value of variable <name>
        for symbol in self.symbols:
            if symbol.name == name:
                return symbol.value
        return None

    def put(self, name, value, init=False):  # puts into memory current value of variable <name>
        for symbol in self.symbols:
            if symbol.name == name:
                symbol.value = value
                return True
        if init==True:
            self.symbols.append(Symbol(name, value))
            return True
        return False
    
    def __str__(self):
        s = "*"
        for symbol in self.symbols:
            s += "("+str(symbol.name)+", "+str(symbol.value)+")"
        s += "#"
        return s

class MemoryStack:
    def __init__(self, memory=None):  # initialize memory stack with memory <memory>
        if memory != None:
            self.stack = [memory]
        else:
            self.stack = []

    def get(self, name):  # get from memory stack current value of variable <name>
        for i in reversed(range(len(self.stack))):
            value = self.stack[i].get(name)
            if value != None:
                return value
        return None

    def insert(self, name, value):  # inserts into memory stack variable <name> with value <value>
        for i in reversed(range(len(self.stack))):
            if self.stack[i].put(name, value)==True:
                break
        else:
            self.stack[-1].put(name, value, init=True)

    def set(self, name, value):   # sets variable <name> to value <value>
        for i in reversed(range(len(self.stack))):
            if self.stack[i].put(name, value)==True:
                break

    def push(self, memory):  # push memory <memory> onto the stack
        self.stack.append(memory)

    def pop(self):  # pops the top memory from the stack
        if self.stack == []:
            return None
        else:
            return self.stack.pop()
            
    def __str__(self):
        s = ""
        for m in self.stack:
            s += m.__str__()
        return s