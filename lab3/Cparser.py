#!/usr/bin/python

from scanner import Scanner
import AST


class Cparser(object):
    def __init__(self):
        self.scanner = Scanner()
        self.scanner.build()
        self.errors = False

    tokens = Scanner.tokens

    precedence = (
        ("nonassoc", 'IFX'),
        ("nonassoc", 'ELSE'),
        ("right", '='),
        ("left", 'OR'),
        ("left", 'AND'),
        ("left", '|'),
        ("left", '^'),
        ("left", '&'),
        ("nonassoc", '<', '>', 'EQ', 'NEQ', 'LE', 'GE'),
        ("left", 'SHL', 'SHR'),
        ("left", '+', '-'),
        ("left", '*', '/', '%'),
    )

    def p_error(self, p):
        self.errors = True
        err_format = "Syntax error at line {0}, column {1}: LexToken({2}, '{3}')"
        if p:
            print(err_format.format(p.lineno, self.scanner.find_tok_column(p), p.type, p.value))
        else:
            print('At end of input')

    def p_program(self, p):
        """program : declarations fundefs instructions"""
        p[0] = AST.Program(p[1], p[2], p[3])

    def p_declarations(self, p):
        """declarations : declarations declaration
                        | """
        if len(p) == 3:
            p[1].declarations.append(p[2])
            p[0] = p[1]
        else:
            p[0] = AST.Declarations()

    def p_declaration(self, p):
        """declaration : TYPE inits ';' 
                       | error ';' """
        if len(p) == 3:
            p[0] = p[1]
        else:
            p[0] = AST.Declaration(p[1], p[2])

    def p_inits(self, p):
        """inits : inits ',' init
                 | init """
        if len(p) == 4:
            p[0] = p[1]
            p[0].inits.append(p[3])
        else:
            p[0] = AST.Inits()
            p[0].inits.append(p[1])

    def p_init(self, p):
        """init : ID '=' expression """
        p[0] = AST.Init(p[1], p[3], p.lineno(1))

    def p_instructions(self, p):
        """instructions : instructions instruction
                        | instruction """
        if len(p) == 3:
            p[1].instructions.append(p[2])
            p[0] = p[1]
        else:
            p[0] = AST.Instructions()
            p[0].instructions.append(p[1])

    def p_instruction(self, p):
        """instruction : print_instr
                       | labeled_instr
                       | assignment
                       | choice_instr
                       | while_instr 
                       | repeat_instr 
                       | return_instr
                       | break_instr
                       | continue_instr
                       | compound_instr"""
        p[0] = p[1]

    def p_print_instr(self, p):
        """print_instr : PRINT expression ';'
                       | PRINT error ';' """
        p[0] = AST.PrintInstr(p[2], p.lineno(1))

    def p_labeled_instr(self, p):
        """labeled_instr : ID ':' instruction """
        p[0] = AST.LabeledInstruction(p[1], p[3], p.lineno(1))

    def p_assignment(self, p):
        """assignment : ID '=' expression ';' """
        p[0] = AST.Assignment(p[1], p[3], p.lineno(1))

    def p_choice_instr(self, p):
        """choice_instr : IF '(' condition ')' instruction  %prec IFX
                        | IF '(' condition ')' instruction ELSE instruction
                        | IF '(' error ')' instruction  %prec IFX
                        | IF '(' error ')' instruction ELSE instruction """
        if len(p) == 8:
            p[0] = AST.IfElseInstr(p[3], p[5], p[7])
        else:
            p[0] = AST.IfInstr(p[3], p[5])

    def p_while_instr(self, p):
        """while_instr : WHILE '(' condition ')' instruction
                       | WHILE '(' error ')' instruction """
        p[0] = AST.WhileInstr(p[3], p[5])

    def p_repeat_instr(self, p):
        """repeat_instr : REPEAT instructions UNTIL condition ';' """
        p[0] = AST.RepeatInstr(p[4], p[2])

    def p_return_instr(self, p):
        """return_instr : RETURN expression ';' """
        p[0] = AST.ReturnInstr(p[2], p.lineno(1))

    def p_continue_instr(self, p):
        """continue_instr : CONTINUE ';' """
        p[0] = AST.ContinueInstr(p.lineno(1))

    def p_break_instr(self, p):
        """break_instr : BREAK ';' """
        p[0] = AST.BreakInstr(p.lineno(1))

    def p_compound_instr(self, p):
        """compound_instr : '{' comp_blocks '}' """
        p[0] = AST.CompoundInstr(p[2])

    def p_condition(self, p):
        """condition : expression"""
        p[0] = p[1]

    def p_const(self, p):
        """const : INTEGER
                 | FLOAT
                 | STRING"""
        lineno = p.lineno(1)
        try:
            int(p[1])
            p[0] = AST.Integer(p[1], lineno)
        except ValueError:
            try:
                float(p[1])
                p[0] = AST.Float(p[1], lineno)
            except ValueError:
                p[0] = AST.String(p[1], lineno)

    def p_id_expr(self, p):
        """expression : ID"""
        p[0] = AST.Variable(p[1], p.lineno(1))

    def p_const_expr(self, p):
        """expression : const"""
        p[0] = p[1]

    def p_paren_expression(self, p):
        """expression : '(' expression ')'
                      | '(' error ')'"""
        p[0] = AST.ParenExpr(p[2])

    def p_funcall(self, p):
        """expression : ID '(' expr_list_or_empty ')'
                      | ID '(' error ')' """
        p[0] = AST.Funcall(p[1], p[3], p.lineno(1))

    def p_bin_expression(self, p):
        """expression : expression '+' expression
                      | expression '-' expression
                      | expression '*' expression
                      | expression '/' expression
                      | expression '%' expression
                      | expression '|' expression
                      | expression '&' expression
                      | expression '^' expression
                      | expression AND expression
                      | expression OR expression
                      | expression SHL expression
                      | expression SHR expression
                      | expression EQ expression
                      | expression NEQ expression
                      | expression '>' expression
                      | expression '<' expression
                      | expression LE expression
                      | expression GE expression"""
        p[0] = AST.BinExpr(p[2], p[1], p[3], p.lineno(2))

    def p_expr_list_or_empty(self, p):
        """expr_list_or_empty : expr_list
                              | """
        p[0] = None if len(p) == 1 else p[1]

    def p_expr_list(self, p):
        """expr_list : expr_list ',' expression
                     | expression """
        p[0] = AST.ExprList()
        if len(p) == 4:
            p[0].cons_expr(p[1].expr_list, p[3])
        else:
            p[0].append_expr(p[1])

    def p_fundefs(self, p):
        """fundefs : fundef fundefs
                   |  """
        p[0] = AST.FundefList()
        if len(p) == 3:
            p[0].cons_fun(p[2].fundef_list, p[1])
        elif len(p) == 2:
            p[0].append_fun(p[1])

    def p_fundef(self, p):
        """fundef : TYPE ID '(' args_list_or_empty ')' compound_instr """
        p[0] = AST.Fundef(p[1], p[2], p[4], p[6], p.lineno(1))

    def p_args_list_or_empty(self, p):
        """args_list_or_empty : args_list
                              | """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = AST.ArgList()  # empty

    def p_args_list(self, p):
        """args_list : args_list ',' arg 
                     | arg """
        p[0] = AST.ArgList()
        if len(p) == 4:
            p[0].cons_arg(p[1].arg_list, p[3])
        else:
            p[0].append_arg(p[1])

    def p_arg(self, p):
        """arg : TYPE ID """
        p[0] = AST.Arg(p[1], p[2], p.lineno(1))