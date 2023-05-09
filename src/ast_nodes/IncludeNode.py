from src.ast_nodes.ASTNode import ASTNode


class IncludeNode(ASTNode):
    def __init__(self, to_include, parent=None, children=None):
        super().__init__(parent, children)
        self.to_include = to_include

    def getLabel(self):
        return "Include: " + self.to_include
