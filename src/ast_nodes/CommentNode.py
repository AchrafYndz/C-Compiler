from src.ast_nodes.ASTNode import ASTNode

class CommentNode(ASTNode):
    def __init__(self, content, parent=None, children=None):
        super().__init__(parent, children)
        self.content = content

    def getLabel(self):
        return "Comment: " + self.content
