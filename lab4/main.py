import sys
import ply.yacc as yacc
from Cparser import Cparser
from TypeChecker import TypeChecker


if __name__ == '__main__':

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    cparser = Cparser()
    parser = yacc.yacc(module=cparser)
    text = file.read()
    ast = parser.parse(text, lexer=cparser.scanner)

    #print ast

    typeChecker = TypeChecker()

    errors, warnings = ast.accept(typeChecker)
    for w in warnings:
        print w

    for er in errors:
        print er