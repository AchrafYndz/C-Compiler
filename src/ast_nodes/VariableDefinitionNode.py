from src.ast_nodes.ASTNode import ASTNode
from src.Type import Type


class VariableDefinitionNode(ASTNode):
    def __init__(self, name, type_, is_array, has_array_size, parent=None, children=None,):
        super().__init__(parent, children)
        self.name: str = name
        self.type: Type = type_
        self.is_array: bool = is_array
        self.has_array_size: bool = has_array_size

    def getLabel(self):
        if self.is_array:
            if not self.has_array_size:
                return "Array Definition: " + self.name + " (" + str(self.type) + ") [with size]"
            else:
                return "Array Definition: " + self.name + " (" + str(self.type) + ") [without size]"
        return "Variable Definition: " + self.name + " (" + str(self.type) + ")"
