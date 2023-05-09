from src.ast_nodes.ASTNode import ASTNode
from src.Util import Type


class TypeDeclarationNode(ASTNode):
    def __init__(self, type_, parent=None, children=None):
        super().__init__(parent, children)
        self.type: Type = type_

    def getLabel(self):
        return "Type Declaration: " + str(self.type)
