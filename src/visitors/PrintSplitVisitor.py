from copy import deepcopy

from src.visitors.ASTVisitor import *


class PrintSplitVisitor(ASTVisitor):
    def __init__(self):
        super().__init__()
        self.visited = []

    def replace_child(self, node: ASTNode, new_children):
        node_index = node.parent.children.index(node)

        for i, new_child in enumerate(new_children):
            self.visited.append(new_child.id)
            if i == 0:
                node.parent.children[node_index] = new_child
                continue
            # insert child
            node.parent.children.insert(node_index+i, new_child)
            new_child.parent = node.parent

    @staticmethod
    def parse_format_string(format_string):
        segments = []
        current_segment = ""
        index = 0
        length = len(format_string)

        while index < length:
            if format_string[index] == '%':
                if current_segment:
                    segments.append(current_segment)
                    current_segment = ""
                current_segment += format_string[index]
                index += 1

                # Check for special format characters
                if index < length and format_string[index] in ['%', 'd', 'i', 's', 'c', 'f']:
                    current_segment += format_string[index]
                    segments.append(current_segment)
                    current_segment = ""
            else:
                current_segment += format_string[index]
            index += 1

        if current_segment:
            segments.append(current_segment)

        return segments

    def visitFunction_call(self, node):
        self.visitChildren(node)
        if node.id in self.visited:
            return
        self.visited.append(node.id)

        if node.name != "printf":
            return

        if len(node.children) == 1:
            return

        format_node = node.children[0]
        format_string = format_node.value

        segments = self.parse_format_string(format_string)
        print(segments)

        new_prints = []
        count = 1
        for i, segment in enumerate(segments):
            segment_children = [LiteralNode(segment, TypeEnum.STRING)]
            if "%" in segment:
                other_child = node.children[count]
                segment_children.append(
                    other_child
                )
                count += 1
            new_print = FunctionCallNode("printf", node.parent, segment_children)
            for child in segment_children:
                child.parent = new_print

            new_prints.append(new_print)

        self.replace_child(node, new_prints)
        print(node)
