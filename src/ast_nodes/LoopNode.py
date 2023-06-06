from src.ast_nodes.ASTNode import ASTNode


class LoopNode(ASTNode):
    def __init__(self, do_while, parent=None, children=None):
        super().__init__(parent, children)
        self.do_while = do_while

    def getLabel(self):
        return "Loop"
