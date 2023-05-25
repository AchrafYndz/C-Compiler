from src.ast_nodes.ASTNode import ASTNode
from src.Type import TypeEnum


class LiteralNode(ASTNode):
    def __init__(self, value, type_, parent=None, children=None):
        super().__init__(parent, children)
        self.value: str = value
        self.type: TypeEnum = type_

    def getLabel(self):
        return f"Literal: {self.value} [{self.type.name}]"
