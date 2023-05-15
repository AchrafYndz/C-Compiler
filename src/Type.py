from enum import Enum


class TypeEnum(Enum):
    VOID = -1
    CHAR = 1
    INT = 2
    FLOAT = 3
    STRING = 4


class Type:
    def __init__(self, type_):
        self.is_const = False
        self.pointer_level = 0
        self.array_size = 0
        self.type: TypeEnum or None = type_

    def __str__(self):
        if self.pointer_level:
            result = ""
            if self.is_const:
                result += "const "
            result += self.type.name + (" *" * self.pointer_level)
        elif self.array_size:
            result = f'{self.type.name}[{self.array_size}]'
        else:
            result = ""
            if self.is_const:
                result += "const "
            result += TypeEnum(self.type).name

        return result