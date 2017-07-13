
class Node(object):

    def __str__(self):
        return self.printTree()


class Program(Node):

    def __init__(self, blocks):
        self.blocks = blocks


class Block(Node):

    def __init__(self, content):
        block_content = []
        if type(content) == list:
            for c in content:
                block_content.append(c)
        else:
            block_content.append(content)
        self.content = block_content


class Declaration(Node):

    def __init__(self, list):
        self.name = 'DECL'
        self.inits = list


class Instruction(Node):

    def __init__(self, name, children):
        self.name = name
        l = []
        for c in children:
            if type(c) == list:
                for i in c:
                    l.append(i)
            else:
                l.append(c)
        self.children = l



class Fundef(Node):

    def __init__(self, type, id, args, comp_instr):
        self.name = 'FUNDEF'
        self.type = type
        self.id = id
        self.args = args
        self.comp_instr = comp_instr


class BinExpr(Node):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class Const(Node):

    def __init__(self, child):
        self.name = 'CONST'
        self.child = child


class Integer(Const):

    def __init__(self, value):
        self.name = 'INTEGER'
        self.value = value


class Float(Const):

    def __init__(self, value):
        self.name = 'FLOAT'
        self.value = value


class String(Const):

    def __init__(self, value):
        self.name = 'STRING'
        self.value = value


class Variable(Node):

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Arg(Node):

    def __init__(self, type, id):
        self.type = type
        self.id = id




# ...


