import pytest
import os
from antlr4 import *

from src.ASTCreator import ASTCreator
from src.ASTErrorListener import ASTErrorListener
from src.antlr.CLexer import CLexer
from src.antlr.CParser import CParser


def test_grammar():
    for directory in ['tests/input/llvm', 'tests/input/semantic_errors']:
        counter = 0
        for filename in os.listdir(directory):
            if filename.endswith('.c'):
                filepath = os.path.join(directory, filename)
                print(f"Now handling {filepath}, which is test {counter}")
                counter += 1
                input_stream = FileStream(filepath)

                lexer = CLexer(input_stream)
                stream = CommonTokenStream(lexer)
                parser = CParser(stream)
                parser.removeErrorListeners()
                parser.addErrorListener(ASTErrorListener())
                tree = parser.program()


def test_ast_creation():
    for directory in ['tests/input/llvm', 'tests/input/semantic_errors']:
        counter = 0
        for filename in os.listdir(directory):
            if filename.endswith('.c'):
                filepath = os.path.join(directory, filename)
                print(f"Now handling {filepath}, which is test {counter}")
                counter += 1
                input_stream = FileStream(filepath)
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
