import pytest
import os
from antlr4 import *

from src.ASTErrorListener import ASTErrorListener
from src.antlr.CLexer import CLexer
from src.antlr.CParser import CParser


def test_llvm():
    for directory in ['tests/input/llvm', 'tests/input/semantic_errors']:
        counter = 0
        fail_counter = 0
        for filename in os.listdir(directory):
            if filename.endswith('.c'):
                filepath = os.path.join(directory, filename)
                print(f"Now handling {filepath}, which is test {counter}")
                try:
                    counter += 1
                    # ast_creator = SemanticAnalysisVisitor()
                    input_stream = FileStream(filepath)

                    lexer = CLexer(input_stream)
                    stream = CommonTokenStream(lexer)
                    parser = CParser(stream)
                    parser.removeErrorListeners()
                    parser.addErrorListener(ASTErrorListener())
                    tree = parser.program()

                    # root = ast_creator.visitProgram(tree)
                    # ast = AST(root)
                    #
                    # file = open("tests/output/llvm/"+filename+".ll", "w+")
                    # assigned = []
                    # ast.toLLVM(file, ast_creator.symbol_table, assigned)
                    # file.close()
                except Exception as e:
                    fail_counter += 1
                    print(f"{filepath} failed: {e}")
                    continue
        print(f"{fail_counter} tests failed")


