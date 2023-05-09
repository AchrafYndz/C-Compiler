from src.ast_nodes.ASTNode import ASTNode


class BinaryExpressionNode(ASTNode):
    def __init__(self, operator, parent=None, children=None):
        super().__init__(parent, children)
        self.operator: str = operator

    def getLabel(self):
        return "Binary Expression: " + self.operator
