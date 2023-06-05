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

    def visitVariable_definition(self, node: VariableDefinitionNode):
        if not node.is_array:
            self.visitChildren(node)
            return

        if node.has_array_size:
            size = int(node.children[0].value)
            self.symbol_table.alter_identifier(node.name, array_size=size)
            self.mips_interface.append_array(node.name, size)
        else:
            self.symbol_table.alter_identifier(node.name, array_size=len(node.children))
            self.mips_interface.append_array(node.name, len(node.children))

    def visitScope(self, node: ScopeNode):
        scope_to_enter = self.symbol_table.get_scope(str(self.scope_counter))
        self.scope_counter += 1

        self.symbol_table.enter_scope(scope_to_enter)
        self.visitChildren(node)
        self.symbol_table.leave_scope()
