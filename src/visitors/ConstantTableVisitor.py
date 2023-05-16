from src.SymbolTable import Scope, SymbolTable
from src.visitors.ASTVisitor import *


class ConstantTableVisitor(ASTVisitor):
    def __init__(self, symbol_table):
        super().__init__()
        self.const_table: {Scope: [{str: str}]} = {}
        self.symbol_table: SymbolTable = symbol_table
        self.scope_counter: int = 1

    def delete_from_table(self, var_name, scope):
        if scope in self.const_table:
            for i, entry in enumerate(self.const_table[scope]):
                if var_name in entry:
                    del self.const_table[scope][i]
                    return
        if scope.parent_scope:
            self.delete_from_table(var_name, scope.parent_scope)

    def visitVariable_definition(self, node: VariableDefinitionNode):
        is_defined = len(node.children) > 0
        if is_defined:
            var_name = node.name
            assignee_node = node.children[0]
            if isinstance(assignee_node, LiteralNode):
                if self.symbol_table.current_scope not in self.const_table:
                    self.const_table[self.symbol_table.current_scope] = []
                self.const_table[self.symbol_table.current_scope].append({var_name: assignee_node.value})
        self.visitChildren(node)

    def visitAssignment(self, node: AssignmentNode):
        var_name = node.name
        self.delete_from_table(var_name, self.symbol_table.current_scope)
        self.visitChildren(node)

    def visitUnary_expression(self, node: UnaryExpressionNode):
        operator = node.operator

        if operator not in ["++", "--"]:
            self.visitChildren(node)
            return

        operand_node = node.children[0]
        if not isinstance(operand_node, VariableNode):
            self.visitChildren(node)
            return

        var_name = operand_node.name
        self.delete_from_table(var_name, self.symbol_table.current_scope)

        self.visitChildren(node)

    def visitFunction_call(self, node: FunctionCallNode):
        func_name = node.name
        if func_name == "printf":
            return
        arg_nodes = node.children
        for arg_node in arg_nodes:
            if not isinstance(arg_node, VariableNode):
                continue
            var_name = arg_node.name
            var_obj = self.symbol_table.get_variable(var_name)
            # a function call could change any variable when it's argument is a pointer
            # therefore the safest option is clearing the table completely after such a function call
            if var_obj.ptr_level > 0:
                self.const_table = {}
        self.visitChildren(node)

    def visitScope(self, node: ScopeNode):
        scope_to_enter = self.symbol_table.get_scope(str(self.scope_counter))
        self.scope_counter += 1

        self.symbol_table.enter_scope(scope_to_enter)
        self.visitChildren(node)
        self.symbol_table.leave_scope()


