from src.visitors.ASTVisitor import *


class OptimizationVisitor(ASTVisitor):
    def __init__(self):
        super().__init__()

    def visitBranch(self, node: BranchNode):
        index = node.parent.children.index(node)
        node.parent.children = node.parent.children[:index + 1]

    def visitConditional(self, node: ConditionalNode):
        condition_node = node.children[0]
        if isinstance(condition_node, LiteralNode) and condition_node.value == "0":
            print("Found conditional that is always false")
            node.parent.children.remove(node)

        self.visitChildren(node)
