import re
from src.Type import TypeEnum, Type

from src.ast_nodes.BranchNode import BranchNode
from src.ast_nodes.LiteralNode import LiteralNode
from src.ast_nodes.VariableNode import VariableNode


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


def look_in_parent(node, node_type, found):
    if node.parent:
        if isinstance(node.parent, node_type):
            found = True
        else:
            found = look_in_parent(node.parent, node_type, found)
    return found


def extract_print_types(print_types):
    regex = r'%[idscf]'
    matches = re.findall(regex, print_types)
    return matches


def extract_scan_types(scan_types):
    regex = r'%[0-9]*[idscf]'
    matches = re.findall(regex, scan_types)
    return matches


def extract_leaves(node, leaves):
    if not node.children:
        leaves.append(node)
    else:
        for child in node.children:
            extract_leaves(child, leaves)


def get_type(node, symbol_table):
    leaves = []
    extract_leaves(node, leaves)
    type_ = -1
    for leaf in leaves:
        if isinstance(leaf, LiteralNode):
            if leaf.type.value > type_:
                type_ = leaf.type.value
        elif isinstance(leaf, VariableNode):
            var_name = leaf.name
            var_obj = symbol_table.get_variable(var_name)
            if var_obj.type_.value > type_:
                type_ = var_obj.type_.value
    enum_type = TypeEnum(type_)
    return enum_type


def cast_to_type(type_, value):
    if type_ == TypeEnum.FLOAT:
        return float(value)
    elif type_ == TypeEnum.INT:
        return int(round(float(value)))
    elif type_ == TypeEnum.CHAR:
        return int(round(float(value))) % 256

    return value
