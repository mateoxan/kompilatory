#!/usr/bin/python
from TreePrinter import TreePrinter
from scanner import Scanner
import AST



class Cparser(object):


    def __init__(self):
        self.scanner = Scanner()
        self.scanner.build()

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
        if p:
            print("Syntax error at line {0}, column {1}: LexToken({2}, '{3}')".format(p.lineno, self.scanner.find_tok_column(p), p.type, p.value))
        else:
            print("Unexpected end of input")


    def p_program(self, p):
        """program : blocks"""
        p[0] = AST.Program(p[1])
        TreePrinter()
        print p[0]

    def p_blocks(self, p):
        """blocks : blocks block
                  | """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []


    def p_block(self, p):
        """block : declaration
                 | instruction
                 | fundef"""
        p[0] = AST.Block(p[1])
                     
    
    def p_declaration(self, p):
        """declaration : TYPE inits ';' 
                       | error ';' """
        if len(p) > 3:
            p[0] = AST.Declaration(p[2])


    def p_inits(self, p):
        """inits : inits ',' init
                 | init """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]


    def p_init(self, p):
        """init : ID '=' expression """
        p[0] = AST.Variable(p[1], p[3])
    
    
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
                       | compound_instr
                       | expression ';' """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = [p[1]]
    
    
    def p_print_instr(self, p):
        """print_instr : PRINT expr_list ';'
                       | PRINT error ';' """
        p[0] = [AST.Instruction(p[1], p[2])]

    
    def p_labeled_instr(self, p):
        """labeled_instr : ID ':' instruction """
        p[0] = [AST.Instruction(p[2], [p[1], p[3]])]
    
    
    def p_assignment(self, p):
        """assignment : ID '=' expression ';' """
        p[0] = [AST.Instruction(p[2], [p[1], p[3]])]
    
    
    def p_choice_instr(self, p):
        """choice_instr : IF '(' condition ')' instruction  %prec IFX
                        | IF '(' condition ')' instruction ELSE instruction
                        | IF '(' error ')' instruction  %prec IFX
                        | IF '(' error ')' instruction ELSE instruction """
        if len(p) == 6:
            p[0] = [AST.Instruction(p[1], [p[3], p[5]])]     #Instruction(IF, [condition, instruction])
        elif len(p) == 8:
            p[0] = [AST.Instruction(p[1], [p[3], p[5]]), AST.Instruction(p[6], [p[7]])]     #Instruction(IF, [condition, instruction])
                                                                                            #Instruction(ELSE, [instruction])
    
    def p_while_instr(self, p):
        """while_instr : WHILE '(' condition ')' instruction
                       | WHILE '(' error ')' instruction """
        p[0] = [AST.Instruction(p[1], [p[3], p[5]])]


    def p_repeat_instr(self, p):
        """repeat_instr : REPEAT instruction UNTIL condition ';' """
        p[0] = [AST.Instruction(p[1], [p[2]]), AST.Instruction(p[3], [p[4]])]
    
    
    def p_return_instr(self, p):
        """return_instr : RETURN expression ';' """
        p[0] = [AST.Instruction(p[1], [p[2]])]

    
    def p_continue_instr(self, p):
        """continue_instr : CONTINUE ';' """
        p[0] = [AST.Instruction(p[1], [])]

    
    def p_break_instr(self, p):
        """break_instr : BREAK ';' """
        p[0] = [AST.Instruction(p[1], [])]
    
    
    def p_compound_instr(self, p):
        """compound_instr : '{' comp_instr_blocks '}' """
        p[0] = p[2]


    def p_comp_instr_blocks(self, p):
        """comp_instr_blocks : comp_instr_blocks comp_instr_block
                             | """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []

    def p_comp_instr_block(self, p):
        """comp_instr_block : declaration
                            | instruction"""
        p[0] = AST.Block(p[1])

    
    def p_condition(self, p):
        """condition : expression"""
        p[0] = p[1]


    def p_const(self, p):
        """const : INTEGER
                 | FLOAT
                 | STRING"""
        if type(p[1]) == int:
            p[0] = AST.Const(AST.Integer(p[1]))
        elif type(p[1]) == float:
            p[0] = AST.Const(AST.Float(p[1]))
        elif type(p[1]) == str:
            p[0] = AST.Const(AST.String(p[1]))
    
    
    def p_expression(self, p):
        """expression : const
                      | ID
                      | expression '+' expression
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
                      | expression GE expression
                      | '(' expression ')'
                      | '(' error ')'
                      | ID '(' expr_list_or_empty ')'
                      | ID '(' error ')' """
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if (p[1] == '('):
                p[0] = p[2]
            else:
                p[0] = AST.BinExpr(p[2], p[1], p[3])
        elif len(p) == 5:
            p[0] = AST.Instruction('FUNCALL', [p[1], p[3]])
    
    
    def p_expr_list_or_empty(self, p):
        """expr_list_or_empty : expr_list
                              | """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = []


    
    def p_expr_list(self, p):
        """expr_list : expr_list ',' expression
                     | expression """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

          
    def p_fundef(self, p):
        """fundef : TYPE ID '(' args_list_or_empty ')' compound_instr """
        p[0] = AST.Fundef(p[1], p[2], p[4], p[6])
    
    
    def p_args_list_or_empty(self, p):
        """args_list_or_empty : args_list
                              | """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = []
    
    def p_args_list(self, p):
        """args_list : args_list ',' arg 
                     | arg """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]
    
    def p_arg(self, p):
        """arg : TYPE ID """
        p[0] = AST.Arg(p[1], p[2])


    