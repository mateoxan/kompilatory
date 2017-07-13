import AST


def addToClass(cls):

    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


class TreePrinter:

    depth=0   #do kontroli wciec

    @addToClass(AST.Node)
    def printTree(self):
        raise Exception("printTree not defined in class " + self.__class__.__name__)


    @addToClass(AST.Program)
    def printTree(self):
        result = ''
        for i in self.blocks:
            result += str(i)
        return result


    @addToClass(AST.Block)
    def printTree(self):
        result = ''
        for i in self.content:        #tutaj moze byc kilka instrukcji (np. if...else...)
            result += '\n' + TreePrinter.depth * '| '+ str(i)
        return result


    @addToClass(AST.BinExpr)
    def printTree(self):
        result = ''
        result += self.op
        TreePrinter.depth += 1
        result += '\n' + TreePrinter.depth*'| ' + str(self.left) + '\n' + TreePrinter.depth*'| ' + str(self.right)
        TreePrinter.depth -= 1
        return result


    @addToClass(AST.Declaration)
    def printTree(self):
        result = ''
        result += self.name
        for i in self.inits:
            TreePrinter.depth += 1
            result += '\n' + str(i)
            TreePrinter.depth -= 1
        return result


    @addToClass(AST.Variable)
    def printTree(self):
        result = ''
        result += TreePrinter.depth * '| ' + '=\n'
        TreePrinter.depth += 1
        result += TreePrinter.depth * '| '
        result += self.name
        result += '\n'+ TreePrinter.depth * '| '
        result += str(self.value)
        TreePrinter.depth -= 1
        return result

    @addToClass(AST.Const)
    def printTree(self):
        return str(self.child)

    @addToClass(AST.Integer)
    def printTree(self):
       return str(self.value)

    @addToClass(AST.Float)
    def printTree(self):
        return str(self.value)

    @addToClass(AST.String)
    def printTree(self):
        return self.value

    @addToClass(AST.Instruction)
    def printTree(self):
        result = ''
        result += self.name
        for c in self.children:
            TreePrinter.depth += 1
            if type(c).__name__ == 'Block':      #jesli w instrukcji jest zagniezdzona inna instrukcja, ten warunek zapobiega podwojnemu wydrukowi wciecia
                result += str(c)
            else:
                result += '\n' + TreePrinter.depth * '| ' + str(c)
            TreePrinter.depth -= 1
        return result

    @addToClass(AST.Fundef)
    def printTree(self):
        result = ''
        result += self.name + '\n'
        TreePrinter.depth += 1
        result += TreePrinter.depth * '| ' + self.id + '\n' + TreePrinter.depth * '| ' + 'RET ' + self.type
        for a in self.args:
            result += '\n' + TreePrinter.depth * '| ' + 'ARG ' + str(a)
        for el in self.comp_instr:
            result += str(el)
        TreePrinter.depth -= 1
        return result

    @addToClass(AST.Arg)
    def printTree(self):
        return self.id
