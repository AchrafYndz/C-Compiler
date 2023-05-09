from src.ast_nodes import ASTNode


class AST:
    def __init__(self, root=None):
        self.root: ASTNode = root

