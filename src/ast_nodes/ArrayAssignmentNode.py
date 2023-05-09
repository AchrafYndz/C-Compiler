from src.ast_nodes.ASTNode import ASTNode


class ArrayAssignmentNode(ASTNode):
    def __init__(self, name, index, parent=None, children=None):
        super().__init__(parent, children)
        self.name: str = name
        self.index: int = index

    def getLabel(self):
        return "Array Assignment: " + self.name + "[" + str(self.index) + "]"
