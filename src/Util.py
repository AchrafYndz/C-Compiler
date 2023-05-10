from enum import Enum

from src.ast_nodes.BranchNode import BranchNode


class TypeEnum(Enum):
    VOID = -1
    CHAR = 1
    INT = 2
    FLOAT = 3
    STRING = 4


class Type:
    def __init__(self, type_):
        self.is_const = False
        self.is_pointer = False
        self.array_size = 0
        self.type: TypeEnum or None = type_

    def __str__(self):
        if self.is_pointer:
            result = self.type.__str__() + " *"
            if self.is_const:
                result += " const"
        elif self.array_size:
            result = f'{self.type.__str__()}[{self.array_size}]'
        else:
            result = ""
            if self.is_const:
                result += "const "
            result += TypeEnum(self.type).name

        return result


def auto_cast(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return ord(value.replace("'", ""))


def returns_something(node, found):
    for child in node.children:
        if isinstance(child, BranchNode):
            if child.sort == "return" and len(child.children) != 0:
                found = True
        found = returns_something(child, found)
    return found

def has_duplicates(arr):
    seen_values = set()
    for value in arr:
        if value in seen_values:
            return True
        seen_values.add(value)
    return False

