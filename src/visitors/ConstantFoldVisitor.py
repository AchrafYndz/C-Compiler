from src.visitors.ASTVisitor import *
from src.Util import get_type, cast_to_type


class ConstantFoldVisitor(ASTVisitor):
    def __init__(self, symbol_table, const_table):
        super().__init__()
        self.symbol_table = symbol_table
        self.const_table = const_table

        self.operations_translation = {
            "&&": "and",
            "||": "or",
            "!": "not"
        }
        self.logical_operations = ["and", "or", "not", ">", "<", ">=", "<=", "==", "!="]

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

    def visitBinary_expression(self, node: BinaryExpressionNode):
        self.visitChildren(node)

        left_node = node.children[0]
        right_node = node.children[1]

        operation = node.operator if node.operator not in self.operations_translation \
            else self.operations_translation[node.operator]

        if isinstance(left_node, LiteralNode) and isinstance(right_node, LiteralNode):
            left_value = left_node.value
            right_value = right_node.value
            type_ = get_type(node, self.symbol_table)

            result = str(eval(f"{left_value} {operation} {right_value}"))

            self.replace_child(node, operation, result, type_)

    def visitUnary_expression(self, node: UnaryExpressionNode):
        self.visitChildren(node)

        operation = node.operator if node.operator not in self.operations_translation \
            else self.operations_translation[node.operator]
        operand_node = node.children[0]

        if isinstance(operand_node, LiteralNode):
            assert(operand_node not in ["++", "--"])
            type_ = get_type(node, self.symbol_table)
            value = operand_node.value

            if node.postfix:
                result = str(eval(f"{value} {operation}"))
            else:
                result = str(eval(f"{operation} {value}"))

            self.replace_child(node, operation, result, type_)

    def visitExplicit_conversion(self, node: ExplicitConversionNode):
        self.visitChildren(node)

        operand_node = node.children[0]

        if isinstance(operand_node, LiteralNode):
            value = operand_node.value
            to_type = node.to_type

            result = str(cast_to_type(to_type, value))

            self.replace_child(node, "", result, to_type)

