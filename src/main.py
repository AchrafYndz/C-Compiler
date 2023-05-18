import sys
from antlr4 import *

from src.antlr.CLexer import CLexer
from src.antlr.CParser import CParser

from src.ASTCreator import ASTCreator
from src.AST import AST
from src.ASTErrorListener import ASTErrorListener
from src.visitors.ConstantTableVisitor import ConstantTableVisitor
from src.visitors.MIPSConversionVisitor import MIPSConversionVisitor

from src.visitors.SemanticAnalysisVisitor import SemanticAnalysisVisitor
from src.visitors.ConstantFoldVisitor import ConstantFoldVisitor


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

    # run semantic analysis
    ast_semantic_visitor = SemanticAnalysisVisitor()
    ast_semantic_visitor.visitScope(root)

    # computing const table
    const_table_visitor = ConstantTableVisitor(
        symbol_table=ast_semantic_visitor.symbol_table
    )
    const_table_visitor.visitScope(root)

    # constant fold
    constant_fold_visitor = ConstantFoldVisitor(
        symbol_table=ast_semantic_visitor.symbol_table,
        const_table=const_table_visitor.const_table
    )
    constant_fold_visitor.visitScope(root)

    root.visualize(filename="test")

    # run semantic analysis
    mips_conversion_visitor = MIPSConversionVisitor()
    mips_conversion_visitor.visitScope(root)
    print(mips_conversion_visitor.content)

    ast = AST(root)


if __name__ == '__main__':
    main(sys.argv)
