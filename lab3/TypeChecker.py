from collections import defaultdict
from SymbolTable import SymbolTable, FunctionSymbol, VariableSymbol
import AST

types_table = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

for op in ['+', '-', '*', '/', '%', '<', '>', '<<', '>>', '|', '&', '^', '<=', '>=', '==', '!=']:
    types_table[op]['int']['int'] = 'int'

for op in ['+', '-', '*', '/']:
    types_table[op]['int']['float'] = 'float'
    types_table[op]['float']['int'] = 'float'
    types_table[op]['float']['float'] = 'float'

for op in ['<', '>', '<=', '>=', '==', '!=']:
    types_table[op]['int']['float'] = 'int'
    types_table[op]['float']['int'] = 'int'
    types_table[op]['float']['float'] = 'int'

types_table['+']['string']['string'] = 'string'
types_table['*']['string']['int'] = 'string'

for op in ['<', '>', '<=', '>=', '==', '!=']:
    types_table[op]['string']['string'] = 'int'

debug = False


class NodeVisitor(object):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        if debug:
            print "Visiting class " + node.__class__.__name__ + " (method: " + visitor.__name__ + ")"
        return visitor(node)

    def generic_visit(self, node):
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            # Some hacking due to wrong attributes' names
            try:
                children = node.children
            except AttributeError:
                try:
                    children = node.declarations
                except AttributeError:
                    try:
                        children = node.instructions
                    except AttributeError:
                        try:
                            children = node.arg_list
                        except AttributeError:
                            try:
                                children = node.fundef_list
                            except AttributeError:
                                try:
                                    children = node.inits
                                except AttributeError:
                                    children = None
            if children is None:
                return
            if not isinstance(children, list):
                self.visit(children)
            else:
                for child in children:
                    if isinstance(child, list):
                        for item in child:
                            if isinstance(item, AST.Node):
                                self.visit(item)
                    elif isinstance(child, AST.Node):
                        self.visit(child)


class TypeChecker(NodeVisitor):
    def __init__(self):
        self.table = SymbolTable(None, "root")
        self.current_type = ""
        self.current_func = None
        self.current_loop = None
        self.errors = False

    def visit_BinExpr(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        t = types_table[op][left][right]
        if t is None:
            self.errors = True
            print "Cannot perform operation {0} between types {1} and {2} at line {3}".format(
                op, left, right, node.lineno
            )
        return t

    def visit_Integer(self, node):
        return 'int'

    def visit_Float(self, node):
        return 'float'

    def visit_String(self, node):
        return 'string'

    def visit_Variable(self, node):
        definition = self.table.getGlobal(node.id)
        if definition is None:
            self.errors = True
            print "Undefined symbol {0} in line {1}.".format(node.id, node.lineno)
        else:
            return definition.type

    def visit_Fundef(self, node):
        f = self.table.get(node.id)
        if f:
            self.errors = True
            if type(f) == FunctionSymbol:
                print "Function {0} is already defined at line {1}. Redefinition at line {2}.".format(
                    node.id, f.lineno, node.lineno
                )
            else:
                print "Name {0} is already defined at line {1}. Redefinition at line {2}.".format(
                    node.id, f.lineno, node.lineno
                )
        else:
            f = FunctionSymbol(node.id, node.t, SymbolTable(self.table, node.id), node.lineno)
            self.table.put(node.id, f)
            self.current_func = f
            globalTable = self.table
            self.table = self.current_func.table
            if node.args_list is not None:
                self.visit(node.args_list)
            self.visit(node.comp_instr)
            self.table = globalTable
            self.current_func = None

    def visit_Assignment(self, node):
        definition = self.table.getGlobal(node.var)
        t = self.visit(node.expr)
        if definition is None:
            self.errors = True
            print "Undefined symbol: {0} at line {1}".format(node.var, node.lineno)
        elif t != definition.type:
            warning = False
            if definition.type == "float" and t == "int":
                warning = True
            self.errors = self.errors or not warning
            print "{0}Wrong assignment type for symbol: {1}: symbol's type is {2}," \
                  " tried to assign type {3} at line {4}.".format("Warning: " if warning else "",
                                                                  node.var, definition.type,
                                                                  t if t is not None else "undefined",
                                                                  node.lineno)

    def visit_Declaration(self, node):
        self.current_type = node.declaration_type
        self.visit(node.inits)
        self.current_type = ""

    def visit_Init(self, node):
        t = self.visit(node.expression)
        if t != self.current_type:
            warning = False
            if t == "int" and self.current_type == "float":
                warning = True
            self.errors = self.errors or not warning
            print "{0}Initialization to symbol {1}: symbol's type is {2}," \
                  " tried to assign type {3} at line {4}".format("Warning: " if Warning else "",
                                                                 node.var_name, self.current_type,
                                                                 t, node.lineno)
        definition = self.table.get(node.var_name)
        if definition is not None:
            self.errors = True
            print "Variable {0} is already defined at line {1}. Redefinition at line {2}.".format(
                node.var_name, definition.lineno, node.lineno
            )
        else:
            self.table.put(node.var_name, VariableSymbol(node.var_name, self.current_type, node.lineno))

    def visit_Arg(self, node):
        definition = self.table.get(node.idd)
        if definition is not None:
            self.errors = True
            print "Argument {0} is already defined at line {1}. Redefinition at line {2}.".format(
                node.idd, definition.lineno, node.lineno
            )
        else:
            self.table.put(node.idd, VariableSymbol(node.idd, node.t, node.lineno))

    def visit_ArgList(self, node):
        for arg in node.arg_list:
            self.visit(arg)
        self.current_func.extract_args()

    def visit_CompoundInstr(self, node):
        innerTable = SymbolTable(self.table, "CompoundScope")
        prevTable = self.table
        self.table = innerTable
        self.visit(node.decls)
        self.visit(node.instrs)
        self.table = prevTable

    def visit_ReturnInstr(self, node):
        f = self.current_func
        if f is None:
            self.errors = True
            print "Return instruction placed outside of function. Line: {0}".format(node.lineno)
            return
        t = self.visit(node.expr)
        if f.type != t:
            warning = False
            if f.type == "float" and t == "int":
                warning = True
            self.errors = self.errors or not warning
            print "{0}Tried to return type {1}, function" \
                  " definition expects type {2}. Line: {3}.".format("Warning: " if warning else "",
                                                                    t, f.type, node.lineno)

    def visit_Funcall(self, node):
        fundef = self.table.getGlobal(node.id)
        if fundef is None or not isinstance(fundef, FunctionSymbol):
            self.errors = True
            print "Undefined function: {0} at line {1}.".format(node.id, node.lineno)
            return None
        if node.expr_list is None:
            if len(fundef.args) != 0:
                self.errors = True
                print "No arguments passed to {0}-argument function {1} at line {2}.".format(
                    len(fundef.args), fundef.name, node.lineno
                )
            return fundef.type
        else:
            if len(fundef.args) != len(node.expr_list.expr_list):
                self.errors = True
                print "Wrong number of arguments ({0}) passed to function {1} (expected: {2}) at line {3}.".format(
                    len(node.expr_list.expr_list), node.id, len(fundef.args), node.lineno)
            else:
                types = [self.visit(x) for x in node.expr_list.expr_list]
                expectedTypes = fundef.args
                i = 1
                for actual, expected in zip(types, expectedTypes):
                    if actual != expected.type:
                        warning = False
                        if actual == "int" and expected.type == "float":
                            warning = True
                        self.errors = self.errors or not warning
                        print "{0}Argument type mismatch (index: {1}, expected: {2}, got: {3}) at line {4}".format(
                            "Warning: " if warning else "", i, expected.type, actual, node.lineno
                        )
                    i += 1
            return fundef.type

    def visit_ParenExpr(self, node):
        return self.visit(node.expression)

    def visit_WhileInstr(self, node):
        self.visit(node.cond)
        prev_loop = self.current_loop
        self.current_loop = node
        self.visit(node.instr)
        self.current_loop = prev_loop

    def visit_RepeatInstr(self, node):
        self.visit(node.cond)
        prev_loop = self.current_loop
        self.current_loop = node
        self.visit(node.instrs)
        self.current_loop = prev_loop

    def visit_BreakInstr(self, node):
        if self.current_loop is None:
            self.errors = True
            print "Break instruction placed outside of loop at line {0}".format(node.lineno)

    def visit_ContinueInstr(self, node):
        if self.current_loop is None:
            self.errors = True
            print "Continue instruction placed outside of loop at line {0}".format(node.lineno)