from src.SymbolTable import SymbolTable, Scope
from src.visitors.ASTVisitor import *
from src.Util import get_type, cast_to_type


class ConstantFoldVisitor(ASTVisitor):
    def __init__(self, symbol_table):
        super().__init__()
        self.symbol_table: SymbolTable = symbol_table
        self.const_table: {Scope: [{str: str}]} = {}
        self.scope_counter: int = 1

        self.operations_translation = {
            "&&": "and",
            "||": "or",
            "!": "not"
        }
        self.logical_operations = ["and", "or", "not", ">", "<", ">=", "<=", "==", "!="]

    def delete_from_table(self, var_name, scope):
        if scope in self.const_table:
            for i, entry in enumerate(self.const_table[scope]):
                if var_name in entry:
                    del self.const_table[scope][i]
                    return
        if scope.parent_scope:
            self.delete_from_table(var_name, scope.parent_scope)

    def get_value_from_const_table(self, var_name, scope):
        if scope in self.const_table:
            for i, entry in enumerate(self.const_table[scope]):
                if var_name in entry:
                    return self.const_table[scope][i][var_name]
        if scope.parent_scope:
            self.get_value_from_const_table(var_name, scope.parent_scope)

    def replace_child(self, node: ASTNode, operation: str, result: str, type_: Type):
        if operation in self.logical_operations:
            result = "0" if result in ["False", "0"] else "1"

        literal_node = LiteralNode(
            value=result,
            type_=type_
        )

        # replace child
        node_index = node.parent.children.index(node)
        node.parent.children[node_index] = literal_node
        literal_node.parent = node.parent

    def visitVariable_definition(self, node: VariableDefinitionNode):
        self.visitChildren(node)
        is_defined = len(node.children) > 0
        if is_defined and not node.is_array:
            var_name = node.name
            assignee_node = node.children[0]
            if isinstance(assignee_node, LiteralNode):
                if self.symbol_table.current_scope not in self.const_table:
                    self.const_table[self.symbol_table.current_scope] = []
                self.const_table[self.symbol_table.current_scope].append({var_name: assignee_node.value})
            elif isinstance(assignee_node, VariableNode):
                value = self.get_value_from_const_table(assignee_node.name, self.symbol_table.current_scope)
                if value:
                    type_ = get_type(assignee_node, self.symbol_table)
                    self.replace_child(assignee_node, None, value, type_)

    def visitAssignment(self, node: AssignmentNode):
        var_name = node.name
        self.delete_from_table(var_name, self.symbol_table.current_scope)
        self.visitChildren(node)

    def visitBinary_expression(self, node: BinaryExpressionNode):
        self.visitChildren(node)

        left_node = node.children[0]
        right_node = node.children[1]

        operation = node.operator if node.operator not in self.operations_translation \
            else self.operations_translation[node.operator]

        left_value = None
        if isinstance(left_node, LiteralNode):
            left_value = left_node.value
        elif isinstance(left_node, VariableNode):
            var_name = left_node.name
            left_value = self.get_value_from_const_table(var_name, self.symbol_table.current_scope)

        right_value = None
        if isinstance(right_node, LiteralNode):
            right_value = right_node.value
        elif isinstance(right_node, VariableNode):
            var_name = right_node.name
            right_value = self.get_value_from_const_table(var_name, self.symbol_table.current_scope)

        if not left_value or not right_value or operation == "[]":
            return

        type_ = get_type(node, self.symbol_table)

        result = str(eval(f"{left_value} {operation} {right_value}"))

        self.replace_child(node, operation, result, type_)

    def visitUnary_expression(self, node: UnaryExpressionNode):
        self.visitChildren(node)

        operation = node.operator if node.operator not in self.operations_translation \
            else self.operations_translation[node.operator]
        operand_node = node.children[0]

        value = None
        if isinstance(operand_node, LiteralNode):
            assert(operand_node not in ["++", "--"])
            value = operand_node.value
        elif isinstance(operand_node, VariableNode):
            var_name = operand_node.name
            value = self.get_value_from_const_table(var_name, self.symbol_table.current_scope)

        if not value or node.operator in ["&", "*"]:
            return

        # TODO: Differentiate between postfix and prefix
        if operation in ["++", "--"]:
            result = str(eval(f"{value} {operation[0]} 1"))
        else:
            result = str(eval(f"{operation} {value}"))

        type_ = get_type(node, self.symbol_table)
        self.replace_child(node, operation, result, type_)

        # Remove variable from const table if it was incremented/decremented
        if node.operator in ["++", "--"]:
            operand_node = node.children[0]
            if isinstance(operand_node, VariableNode):
                var_name = operand_node.name
                self.delete_from_table(var_name, self.symbol_table.current_scope)

    def visitFunction_call(self, node: FunctionCallNode):
        func_name = node.name
        if func_name != "printf":
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
        if func_name == "scanf":
            args_children = node.children[1:]
            for child in args_children:
                if isinstance(child, VariableNode):
                    self.delete_from_table(child.name, self.symbol_table.current_scope)
        self.visitChildren(node)

    def visitExplicit_conversion(self, node: ExplicitConversionNode):
        self.visitChildren(node)

        operand_node = node.children[0]

        if isinstance(operand_node, LiteralNode):
            value = operand_node.value
            to_type = node.to_type

            result = str(cast_to_type(to_type, value))

            self.replace_child(node, "", result, to_type)

    def visitScope(self, node: ScopeNode):
        scope_to_enter = self.symbol_table.get_scope(str(self.scope_counter))
        self.scope_counter += 1

        self.symbol_table.enter_scope(scope_to_enter)
        self.visitChildren(node)
        self.symbol_table.leave_scope()
