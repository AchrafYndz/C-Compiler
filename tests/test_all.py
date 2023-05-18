import pytest
import os
from antlr4 import *

from src.ASTCreator import ASTCreator
from src.ASTErrorListener import ASTErrorListener
from src.antlr.CLexer import CLexer
from src.antlr.CParser import CParser
from src.visitors.SemanticAnalysisVisitor import SemanticAnalysisVisitor


def test_ast_creation():
    directory = 'tests/input/mips'
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

            ast_semantic_visitor = SemanticAnalysisVisitor()
            # run semantic analysis
            ast_semantic_visitor.visitScope(root)


def test_semantic_analysis():
    directory = 'tests/input/semantic_errors'
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

            root.visualize(filename="semantic_test")

            with pytest.raises(Exception) as exception:
                ast_semantic_visitor = SemanticAnalysisVisitor()
                # run semantic analysis
                ast_semantic_visitor.visitScope(root)
            print(f"{exception.typename}: {exception.value}")
