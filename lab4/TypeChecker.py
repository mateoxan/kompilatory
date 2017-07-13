#!/usr/bin/python
from SymbolTable import SymbolTable
from Types import ttype


class ArgInFundef(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type


class TypeChecker(object):
    errors = []
    warnings = []

    def visit_BinExpr(self, node):
        node.left.Scope = node.Scope
        node.right.Scope = node.Scope
        type1 = node.left.accept(self)
        type2 = node.right.accept(self)
        if ttype[node.op][type1][type2] != {}:
            return ttype[node.op][type1][type2]
        else:
            self.errors.append(
                "Invalid types of expression: {} {} {}, line {}".format(type1, node.op, type2, node.lineno))
            return 'int'

    def visit_Const(self, node):
        pass

    def visit_Integer(self, node):
        return 'int'

    def visit_Float(self, node):
        return 'float'

    def visit_String(self, node):
        return 'string'

    def visit_Variable(self, node):
        if node.Scope.getVariable(node.name) == None:
            self.errors.append("Variable {} not initialised, line {}".format(node.name, node.lineno))
        else:
            return node.Scope.getVariable(node.name)


    def visit_Funcall(self, node):
        type1 = node.Scope.getFunction(node.name)

        if len(node.args) != len(node.Scope.getFunctionArgs(node.name)):
            self.errors.append("Invalid number of arguments in function {}, line {}".format(node.name, node.lineno))
        else:
            for i in xrange(0, len(node.args)):
                arg = node.args[i]
                arg.Scope = node.Scope
                type1 = arg.accept(self)
                type2 = node.Scope.getFunctionArgs(node.name)[i].type
                if ttype['='][type2][type1] == {}:
                    self.errors.append(
                        "Invalid argument {} in function {} type {} supposed to be {}, line {}".format(i, node.name,
                                                                                                       type1, type2,
                                                                                                       node.lineno))

        return type1

    def visit_If(self, node):
        node.condition.Scope = node.Scope
        node.condition.accept(self)
        node.instruction.Scope = SymbolTable(node.Scope)
        node.instruction.accept(self)


    def visit_IfElse(self, node):
        node.condition.Scope = node.Scope
        node.condition.accept(self)
        node.instruction1.Scope = SymbolTable(node.Scope)
        node.instruction1.accept(self)
        node.instruction2.Scope = SymbolTable(node.Scope)
        node.instruction2.accept(self)


    def visit_NoArgInstruction(self, node):
        pass


    def visit_Continue(self, node):
        pass


    def visit_Break(self, node):
        pass


    def visit_OneArgInstruction(self, node):
        node.arg.Scope = node.Scope
        node.arg.accept(self)


    def visit_Print(self, node):
        node.arg.Scope = node.Scope
        node.arg.accept(self)


    def visit_Return(self, node):
        node.arg.Scope = node.Scope
        node.arg.accept(self)


    def visit_While(self, node):
        node.condition.Scope = node.Scope
        node.condition.accept(self)
        node.instruction.Scope = SymbolTable(node.Scope)
        node.instruction.accept(self)

    def visit_Fundef(self, node):
        a = []
        for i in xrange(0, len(node.arguments)):
            arg = node.arguments[i]
            a.append(ArgInFundef(arg.name, arg.type))
            node.Scope.putVariable(arg.name, arg.type)
        node.Scope.putFunction(node.name, node.type, a)
        Scope = SymbolTable(node.Scope)

        node.instructions.Scope = Scope
        node.instructions.accept(self)


    def visit_Argument(self, node):
        return node.name, node.type


    def visit_Declaration(self, node):
        for init in node.inits:
            init.Scope = node.Scope
            self.visit_Init(init, node.type)


    def visit_Program(self, node):
        node.Scope = SymbolTable(None)

        for decl in node.declarations:
            decl.Scope = node.Scope
            decl.accept(self)

        for fundef in node.fundefs:
            fundef.Scope = node.Scope
            fundef.accept(self)

        for instr in node.instructions:
            instr.Scope = node.Scope
            instr.accept(self)

        return self.errors, self.warnings


    def visit_CompoundInstructions(self, node):
        for decl in node.declarations:
            decl.Scope = node.Scope
            decl.accept(self)

        for instr in node.instructions:
            instr.Scope = node.Scope
            instr.accept(self)


    def visit_Labeled(self, node):
        node.instruction.Scope = node.Scope
        node.instruction.accept(self)


    def visit_Assignment(self, node):
        node.expression.Scope = node.Scope
        type1 = node.expression.accept(self)
        if type1 == None:
            self.errors.append("Incorrect expression, line {}".format(node.lineno))
        type2 = node.Scope.getVariable(node.name)
        if type2 == None:
            self.errors.append("Variable {} was not declared, line {}".format(node.name, node.lineno))
        if ttype['='][type1][type2] == {}:
            self.errors.append("Invalid assignment of {}, line {}".format(node.name, node.lineno))


    def visit_Init(self, node, type):
        if node.Scope.putVariable(node.name, type) == False:
            self.warnings.append("Variable {} was already initialized, line {}".format(node.name, node.lineno))


    def visit_Repeat(self, node):
        Scope = SymbolTable(node.Scope)
        for instr in node.instructions:
            instr.Scope = Scope
            instr.accept(self)

        node.condition.Scope = Scope
        node.condition.accept(self)
