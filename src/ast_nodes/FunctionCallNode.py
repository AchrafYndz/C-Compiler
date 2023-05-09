from src.ast_nodes.ASTNode import ASTNode


class FunctionCallNode(ASTNode):
    def __init__(self, name, parent=None, children=None):
        super().__init__(parent, children)
        self.name = name

    def getLabel(self):
        return "Function Call: " + self.name
