import sys
from antlr4 import *

from src.antlr.CLexer import CLexer
from src.antlr.CParser import CParser

from src.ASTCreator import ASTCreator
from src.AST import AST
from src.ASTErrorListener import ASTErrorListener


def main(argv):
    input_stream = FileStream(argv[1])
    lexer = CLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)
    tree = parser.program()

    parser.removeErrorListeners()
    parser.addErrorListener(ASTErrorListener())

    walker = ParseTreeWalker()
    ast_creator = ASTCreator()
    walker.walk(ast_creator, tree)

    # create AST tree
    ast_creator.enterProgram(tree)
    root = ast_creator.root

    root.visualize(filename="test")

    ast = AST(root)


if __name__ == '__main__':
    main(sys.argv)
