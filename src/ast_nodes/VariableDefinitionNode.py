from src.ast_nodes.ASTNode import ASTNode
from src.Util import Type


class VariableDefinitionNode(ASTNode):
    def __init__(self, name, type_, is_array, parent=None, children=None,):
        super().__init__(parent, children)
        self.name: str = name
        self.type: Type = type_
        self.is_array: bool = is_array

    def getLabel(self):
        if self.is_array:
            return "Array Definition: " + self.name + " (" + str(self.type) + ")"
        return "Variable Definition: " + self.name + " (" + str(self.type) + ")"
