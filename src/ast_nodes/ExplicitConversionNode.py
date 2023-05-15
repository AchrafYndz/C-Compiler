from src.Type import TypeEnum
from src.ast_nodes.ASTNode import ASTNode


class ExplicitConversionNode(ASTNode):
    def __init__(self, to_type, parent=None, children=None):
        super().__init__(parent, children)
        self.to_type: TypeEnum = to_type

    def getLabel(self):
        return "Explicit Conversion: " + str(self.to_type.name)
