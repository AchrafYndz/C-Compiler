import sys
import subprocess
from antlr4 import *

from src.antlr.CLexer import CLexer
from src.antlr.CParser import CParser

from src.ASTCreator import ASTCreator
from src.AST import AST
from src.ASTErrorListener import ASTErrorListener
from src.visitors.MIPSConversionVisitor import MIPSConversionVisitor

from src.visitors.SemanticAnalysisVisitor import SemanticAnalysisVisitor
from src.visitors.ConstantFoldVisitor import ConstantFoldVisitor


RUN_MIPS = False


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
    ast = AST(ast_creator.root)

    # run semantic analysis
    ast_semantic_visitor = SemanticAnalysisVisitor()
    ast_semantic_visitor.visitScope(ast.root)

    # constant fold
    constant_fold_visitor = ConstantFoldVisitor(
        symbol_table=ast_semantic_visitor.symbol_table
    )
    constant_fold_visitor.visitScope(ast.root)
    print(constant_fold_visitor.const_table)

    ast.visualize(filename="test")

    # generate mips code
    if RUN_MIPS:
        mips_conversion_visitor = MIPSConversionVisitor(
            symbol_table=ast_semantic_visitor.symbol_table,
        )
        mips_conversion_visitor.visitScope(ast.root)
        mips_conversion_visitor.mips_interface.write_to_file("tests/output/mips/test.asm")

        print("----------------------------------------")
        print("Running Mips...")
        print("----------------------------------------")
        subprocess.call(["java", "-jar", "bin/Mars4_5.jar", "tests/output/mips/test.asm"])


if __name__ == '__main__':
    main(sys.argv)
