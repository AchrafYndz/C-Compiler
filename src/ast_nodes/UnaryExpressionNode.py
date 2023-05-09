from src.ast_nodes.ASTNode import ASTNode


class UnaryExpressionNode(ASTNode):
    def __init__(self, operator, postfix=False, parent=None, children=None):
        super().__init__(parent, children)
        self.operator: str = operator
        self.postfix: bool = postfix

    def getLabel(self):
        return "Unary Expression: " + self.operator
