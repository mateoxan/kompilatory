import AST

indent_char = '| '


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


class TreePrinter:
    @addToClass(AST.Node)
    def printTree(self, indent=0):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @addToClass(AST.BinExpr)
    def printTree(self, indent=0):
        res = indent_char * indent
        res += self.op + '\n'
        res += self.left.printTree(indent + 1) if isinstance(self.left, (AST.Expression, AST.Const))\
            else indent_char * (indent + 1) + self.left
        res += self.right.printTree(indent + 1) if isinstance(self.right, (AST.Expression, AST.Const))\
            else indent_char * (indent + 1) + self.right
        return res

    @addToClass(AST.Program)
    def printTree(self, indent=0):
        res = ""
        res += self.declarations.printTree(indent)
        res += self.fundefs.printTree(indent)
        res += self.instructions.printTree(indent)
        return res

    @addToClass(AST.Arg)
    def printTree(self, indent=0):
        res = indent * indent_char
        res += "ARG " + self.idd + '\n'
        return res

    @addToClass(AST.ArgList)
    def printTree(self, indent=0):
        res = ""
        for argg in self.arg_list:
            res += argg.printTree(indent)
        return res

    @addToClass(AST.Assignment)
    def printTree(self, indent=0):
        res = indent * indent_char + "=\n"
        res += indent_char * (indent + 1) + self.var + "\n"
        res += self.expr.printTree(indent + 1) if isinstance(self.expr, (AST.Expression, AST.Const))\
            else indent_char * (indent + 1) + self.expr
        return res

    @addToClass(AST.BreakInstr)
    def printTree(self, indent=0):
        return indent * indent_char + " BREAK\n"

    @addToClass(AST.Integer)
    def printTree(self, indent=0):
        res = indent * indent_char
        res += self.val
        return res + "\n"

    @addToClass(AST.Float)
    def printTree(self, indent=0):
        res = indent * indent_char
        res += self.val
        return res + "\n"

    @addToClass(AST.String)
    def printTree(self, indent=0):
        res = indent * indent_char
        res += self.val
        return res + "\n"

    @addToClass(AST.CompoundInstr)
    def printTree(self, indent=0):
        res = self.decls.printTree(indent)
        res += self.instrs.printTree(indent)
        return res

    @addToClass(AST.ContinueInstr)
    def printTree(self, indent=0):
        return indent * indent_char + " CONTINUE\n"


    @addToClass(AST.Declaration)
    def printTree(self, indent=0):
        res = indent * indent_char + "DECL\n"
        res += self.inits.printTree(indent + 1)
        return res

    @addToClass(AST.Declarations)
    def printTree(self, indent=0):
        res = ""
        for d in self.declarations:
            res += d.printTree(indent)
        return res

    @addToClass(AST.Init)
    def printTree(self, indent=0):
        res = indent * indent_char + "=\n"
        res += (indent + 1) * indent_char + self.var_name + "\n"
        res += self.expression.printTree(indent + 1)
        return res

    @addToClass(AST.Inits)
    def printTree(self, indent=0):
        res = ""
        for i in self.inits:
            res += i.printTree(indent)
        return res

    @addToClass(AST.Empty)
    def printTree(self, indent=0):
        return ""

    @addToClass(AST.ExprList)
    def printTree(self, indent=0):
        res = ""
        for e in self.expr_list:
            res += e.printTree(indent)
        return res

    @addToClass(AST.Funcall)
    def printTree(self, indent=0):
        res = indent * indent_char + "FUNCALL\n"
        res += (indent + 1) * indent_char + self.id + "\n"
        if self.expr_list is not None:
            res += self.expr_list.printTree(indent+1)
        return res

    @addToClass(AST.Variable)
    def printTree(self, indent=0):
        res = indent * indent_char
        res += self.id + '\n'
        return res

    @addToClass(AST.IfInstr)
    def printTree(self, indent=0):
        res = indent * indent_char + "IF\n"
        res += self.cond.printTree(indent + 1)
        res += self.instr.printTree(indent + 1)
        return res

    @addToClass(AST.IfElseInstr)
    def printTree(self, indent=0):
        res = indent * indent_char + "IF\n"
        res += self.cond.printTree(indent + 1)
        res += self.instr.printTree(indent + 1)
        res += indent * indent_char + "ELSE\n"
        res += self.elseinstr.printTree(indent + 1)
        return res

    @addToClass(AST.WhileInstr)
    def printTree(self, indent=0):
        res = indent * indent_char + "WHILE\n"
        res += self.cond.printTree(indent + 1)
        res += self.instr.printTree(indent + 1)
        return res

    @addToClass(AST.RepeatInstr)
    def printTree(self, indent=0):
        res = indent * indent_char + "REPEAT\n"
        res += self.cond.printTree(indent + 1)
        res += self.instrs.printTree(indent + 1)
        return res

    @addToClass(AST.ReturnInstr)
    def printTree(self, indent=0):
        res = indent * indent_char + "RETURN\n"
        res += self.expr.printTree(indent + 1) if isinstance(self.expr, (AST.Expression, AST.Const))\
            else (indent + 1) * indent_char + self.expr
        return res

    @addToClass(AST.PrintInstr)
    def printTree(self, indent=0):
        res = indent * indent_char + "PRINT\n"
        res += self.to_print.printTree(indent + 1) if isinstance(self.to_print, (AST.Expression, AST.Const))\
            else (indent + 1) * indent_char + self.to_print
        return res

    @addToClass(AST.LabeledInstruction)
    def printTree(self, indent=0):
        res = self.label.printTree(indent) + "\n"
        res += self.instr.printTree(indent + 1)
        return res

    @addToClass(AST.Instructions)
    def printTree(self, indent=0):
        res = ""
        for i in self.instructions:
            res += i.printTree(indent)
        return res

    @addToClass(AST.ParenExpr)
    def printTree(self, indent=0):
        # nie wypisujemy nawiasow w ASt, wiec w sumie to samo, co zwykle expression
        to_ret = self.expression.printTree(indent) if isinstance(self.expression, (AST.Expression, AST.Const))\
            else indent * indent_char + self.expression
        return to_ret

    @addToClass(AST.Fundef)
    def printTree(self, indent=0):
        res = indent * indent_char + "FUNDEF\n"
        res += (indent + 1) * indent_char + self.id + "\n"
        res += (indent + 1) * indent_char + "RET " + self.t + "\n"
        res += self.args_list.printTree(indent + 1)
        res += self.comp_instr.printTree(indent + 1)
        return res

    @addToClass(AST.FundefList)
    def printTree(self, indent=0):
        res = ""
        for f in self.fundef_list:
            res += f.printTree(indent)
        return res
