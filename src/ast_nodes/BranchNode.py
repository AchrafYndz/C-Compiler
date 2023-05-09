from src.ast_nodes.ASTNode import ASTNode


class BranchNode(ASTNode):
    def __init__(self, sort, parent=None, children=None):
        super().__init__(parent, children)
        self.sort: str = sort

    def getLabel(self):
        return "Branch: " + self.sort
