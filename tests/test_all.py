import subprocess
from threading import Thread

import pytest
import os
from antlr4 import *

from src.AST import AST
from src.ASTCreator import ASTCreator
from src.ASTErrorListener import ASTErrorListener
from src.MIPSConverter import MIPSConverter
from src.antlr.CLexer import CLexer
from src.antlr.CParser import CParser
from src.visitors.ConstantFoldVisitor import ConstantFoldVisitor
from src.visitors.OptimizationVisitor import OptimizationVisitor
from src.visitors.PrintSplitVisitor import PrintSplitVisitor
from src.visitors.SemanticAnalysisVisitor import SemanticAnalysisVisitor
from src.visitors.TranslationVisitor import TranslationVisitor


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
            ast = AST(ast_creator.root)

            # catch semantic errors
            with pytest.raises(SystemExit):
                ast_semantic_visitor = SemanticAnalysisVisitor()
                # run semantic analysis
                ast_semantic_visitor.visitScope(ast.root)


def test_valid():
    directory = 'tests/input/valid'
    counter = 0
    for filename in os.listdir(directory):
        if filename.endswith('.c'):
            filepath = os.path.join(directory, filename)
            base_name = filename[:-2]
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
            ast = AST(ast_creator.root)

            # translate for to while
            translator = TranslationVisitor()
            translator.visitScope(ast.root)

            # split printf formatting
            print_splitter = PrintSplitVisitor()
            print_splitter.visitScope(ast.root)

            # run optimizer
            optimizer = OptimizationVisitor()
            optimizer.visitScope(ast.root)

            # run semantic analysis
            ast_semantic_visitor = SemanticAnalysisVisitor()
            ast_semantic_visitor.visitScope(ast.root)

            # constant fold
            constant_fold_visitor = ConstantFoldVisitor(
                symbol_table=ast_semantic_visitor.symbol_table
            )
            constant_fold_visitor.visitScope(ast.root)

            # generate DOT file
            ast.visualize(filename="valid")

            # generate mips code
            mips_converter = MIPSConverter(
                symbol_table=ast_semantic_visitor.symbol_table,
            )
            mips_converter.convert(ast.root, base_name)

            subprocess.call(
                f"java -jar bin/Mars4_5.jar tests/output/mips/{base_name}.asm > tests/output/mips/{base_name}.out",
                shell=True
            )


def test_mips():
    directory = 'tests/input/mips'
    counter = 0
    for filename in os.listdir(directory):
        if filename.endswith('.c'):
            filepath = os.path.join(directory, filename)
            base_name = filename[:-2]
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
            ast = AST(ast_creator.root)

            # run semantic analysis
            ast_semantic_visitor = SemanticAnalysisVisitor()
            ast_semantic_visitor.visitScope(ast.root)

            # run optimizer
            optimizer = OptimizationVisitor()
            optimizer.visitScope(ast.root)

            # constant fold
            constant_fold_visitor = ConstantFoldVisitor(
                symbol_table=ast_semantic_visitor.symbol_table
            )
            constant_fold_visitor.visitScope(ast.root)

            # generate DOT file
            ast.visualize(filename="valid")

            # generate mips code
            mips_converter = MIPSConverter(
                symbol_table=ast_semantic_visitor.symbol_table,
            )
            mips_converter.convert(ast.root, base_name)

            subprocess.call(
                f"java -jar bin/Mars4_5.jar tests/output/mips/{base_name}.asm > tests/output/mips/{base_name}.out",
                shell=True
            )
