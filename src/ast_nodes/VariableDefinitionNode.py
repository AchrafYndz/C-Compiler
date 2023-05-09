from src.ast_nodes.ASTNode import ASTNode
from src.Util import Type


class VariableDefinitionNode(ASTNode):
    def __init__(self, name, type_, parent=None, children=None,):
        super().__init__(parent, children)
        self.name: str = name
        self.type: Type = type_

    def getLabel(self):
        return "Variable Definition: " + self.name + " (" + str(self.type) + ")"
