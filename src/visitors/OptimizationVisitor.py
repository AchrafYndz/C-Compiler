from src.visitors.ASTVisitor import *


class OptimizationVisitor(ASTVisitor):
    def __init__(self):
        super().__init__()

    def visitBranch(self, node: BranchNode):
        index = node.parent.children.index(node)
        node.parent.children = node.parent.children[:index+1]
