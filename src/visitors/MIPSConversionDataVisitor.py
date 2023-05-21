from src.SymbolTable import SymbolTable
from src.ast_nodes import *
from src.visitors.ASTVisitor import ASTVisitor
from src.MIPSInterface import MIPSInterface


class MIPSConversionDataVisitor(ASTVisitor):
    def __init__(self, symbol_table: SymbolTable, mips_interface):
        super().__init__()
        self.symbol_table = symbol_table
        self.scope_counter: int = 1
        self.mips_interface = mips_interface

    def visitLiteral(self, node: LiteralNode):
        if node.type == TypeEnum.STRING:
            self.mips_interface.append_string(node.value)
        self.visitChildren(node)
