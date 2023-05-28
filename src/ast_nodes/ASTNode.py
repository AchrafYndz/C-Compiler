import itertools
from graphviz import Source


class ASTNode:
    next_id = itertools.count()

    def __init__(self, parent=None, children=None):
        if children is None:
            children = []
        self.parent: ASTNode or None = parent
        self.children: list[ASTNode] = children
        self.id = next(ASTNode.next_id)

    def getLabel(self):
        return "Template Node"

    def visualize(self, filename=None, file=None):
        if self.parent:
            file.write("subgraph { " + str(self.parent.id) + " [label=\"" + self.parent.getLabel().replace('"', '\\"') + "\"];} "
                        "-> subgraph {" + str(self.id) + " [label=\"" + self.getLabel().replace('"', '\\"') + "\"];};\n")
        else:
            file = open(f"visualization/{filename}.dot", "w+")
            file.write("digraph AST {\nrankdir=LR\n")

        for child in self.children:
            child.visualize(file=file)

        if not self.parent:
            file.write("}")
            file.close()

            dot_file = Source.from_file(f"visualization/{filename}.dot")
            dot_file.render(filename=filename, directory="visualization/", format="pdf", cleanup=True, view=False)

    def addChild(self, child, index=-1):
        child.parent = self
        if index == -1:
            self.children.append(child)
        else:
            self.children.insert(index, child)
