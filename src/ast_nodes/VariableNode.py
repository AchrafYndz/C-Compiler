from src.ast_nodes.ASTNode import ASTNode


class VariableNode(ASTNode):
    def __init__(self, name, parent=None, children=None):
        super().__init__(parent, children)
        self.name: str = name

    def getLabel(self):
        return "Variable: " + self.name
