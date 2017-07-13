#!/usr/bin/python

class Fun(object):
    def __init__(self,args,type):
        self.args = args
        self.type = type

class SymbolTable(object):
    def __init__(self, parent):  # parent scope
        self.parent = parent
        self.variables = {}
        self.functions = {}

    def putFunction(self,name,type,args):
        if name in self.functions.keys():
            self.functions[name] = Fun(args,type)
            return False
        else:
            self.functions[name] = Fun(args,type)
            return True

    def getFunction(self,name):
        if name in self.functions.keys():
            return self.functions[name].type
        elif self.parent != None:
            return self.getParentScope().getFunction(name)
        else:
            return None

    def getFunctionArgs(self,name):
        if name in self.functions.keys():
            return self.functions[name].args
        elif self.parent != None:
            return self.getParentScope().getFunctionArgs(name)
        else:
            return None

    def putVariable(self, name, type):  # put variable type under <name> entry
        if name in self.variables.keys():
            self.variables[name] = type
            return False
        else:
            self.variables[name] = type
            return True

    def getVariable(self, name):  # get variable type from <name> entry
        if name in self.variables.keys():
            return self.variables[name]
        elif self.parent != None:
            return self.getParentScope().getVariable(name)
        else:
            return None


    def getParentScope(self):
        return self.parent