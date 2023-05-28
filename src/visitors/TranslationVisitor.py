from src.visitors.ASTVisitor import *


class TranslationVisitor(ASTVisitor):
    """
    Translates for-loops to while-loops
    """
    def __init__(self):
        super().__init__()
        self.visited = []

    def visitLoop(self, node: LoopNode):
        if node.id in self.visited:
            return
        self.visited.append(node.id)

        is_for_loop = len(node.children) > 2
        if not is_for_loop:
            self.visitChildren(node)
            return

        initialization = node.children[0]
        node.parent.addChild(initialization, index=0)
        node.children.remove(initialization)

        loop_statement = node.children[-2]
        scope_node = node.children[-1]

        scope_node.addChild(loop_statement)
        node.children.remove(loop_statement)

        self.visitChildren(node)
