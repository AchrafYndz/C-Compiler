from src.ast_nodes.ASTNode import ASTNode


class FunctionArgumentNode(ASTNode):
    def __init__(self, type_, name, parent=None, children=None):
        super().__init__(parent, children)
        self.type = type_
        self.name = name

    def getLabel(self):
        return "Function Argument: " + self.name + " (" + str(self.type) + ")"
