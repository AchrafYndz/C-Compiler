from src.ast_nodes.ASTNode import ASTNode
from src.Util import Type


class LiteralNode(ASTNode):
    def __init__(self, value, type_, parent=None, children=None):
        super().__init__(parent, children)
        self.value: str = value
        self.type: Type = type_

    def getLabel(self):
        return "Literal: " + self.value
