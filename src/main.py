import argparse
import sys
import subprocess
from antlr4 import *

from src.MIPSConverter import MIPSConverter
from src.antlr.CLexer import CLexer
from src.antlr.CParser import CParser

from src.ASTCreator import ASTCreator
from src.AST import AST
from src.ASTErrorListener import ASTErrorListener
from src.visitors.OptimizationVisitor import OptimizationVisitor
from src.visitors.PrintSplitVisitor import PrintSplitVisitor

from src.visitors.SemanticAnalysisVisitor import SemanticAnalysisVisitor
from src.visitors.ConstantFoldVisitor import ConstantFoldVisitor
from src.visitors.TranslationVisitor import TranslationVisitor


def run(input_file, visualize, run_mips):
    input_stream = FileStream(input_file)
    lexer = CLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)

    parser.removeErrorListeners()
    parser.addErrorListener(ASTErrorListener())

    tree = parser.program()

    walker = ParseTreeWalker()
    ast_creator = ASTCreator()
    walker.walk(ast_creator, tree)

    # create AST tree
    ast_creator.enterProgram(tree)
    ast = AST(ast_creator.root)

    # translate for to while
    translator = TranslationVisitor()
    translator.visitScope(ast.root)

    # split printf formatting
    print_splitter = PrintSplitVisitor()
    print_splitter.visitScope(ast.root)

    # run semantic analysis
    ast_semantic_visitor = SemanticAnalysisVisitor()
    ast_semantic_visitor.visitScope(ast.root)

    # constant fold
    constant_fold_visitor = ConstantFoldVisitor(
        symbol_table=ast_semantic_visitor.symbol_table
    )
    constant_fold_visitor.visitScope(ast.root)

    # optimize
    optimizer = OptimizationVisitor()
    optimizer.visitScope(ast.root)

    if visualize:
        # visualize the ast
        ast.visualize(filename="test")

    # generate mips code
    mips_converter = MIPSConverter(
        symbol_table=ast_semantic_visitor.symbol_table,
    )
    mips_converter.convert(ast.root, "test")

    if run_mips:
        # run the generated Mips code using Mars
        print("----------------------------------------")
        print("Running Mips...")
        print("----------------------------------------")
        subprocess.call(["java", "-jar", "bin/Mars4_5.jar", "tests/output/mips/test.asm"])


def main():
    parser = argparse.ArgumentParser(prog='C-Compiler', description='Compiles C-code to MIPS assembly.')
    parser.add_argument('input_file', help='Input file for your program')
    parser.add_argument('-r', '--run', action='store_true', help='Run the generated MIPS assembly code using MARS')
    parser.add_argument('-v', '--visualize', action='store_true', help='Visualize the Abstract Syntax Tree')
    args = parser.parse_args()
    run(
        input_file=args.input_file,
        visualize=args.visualize,
        run_mips=args.run
    )


if __name__ == '__main__':
    main()
