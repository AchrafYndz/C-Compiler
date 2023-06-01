from src.ast_nodes.ASTNode import ASTNode


class ConditionalNode(ASTNode):
    def __init__(self, parent=None, children=None, has_else=False):
        self.has_else = has_else
        super().__init__(parent, children)

    def getLabel(self):
        return "Conditional"
