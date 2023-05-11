from src.ast_nodes.ASTNode import ASTNode


class LoopNode(ASTNode):
    def __init__(self, parent=None, children=None):
        super().__init__(parent, children)

    def getLabel(self):
        return "Loop"