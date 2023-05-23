from src.Type import TypeEnum
from MIPSInterface import MIPSInterface


INSTRUCTIONS = {
    '+': MIPSInterface.add_unsigned,
    '-': MIPSInterface.subtract_unsigned,
    '*': MIPSInterface.multiply,
    '/': MIPSInterface.divide,
    '%': MIPSInterface.modulo,
    '<': MIPSInterface.strictly_less,
    '>': MIPSInterface.strictly_greater,
    '<=': MIPSInterface.less_or_equal,
    '>=': MIPSInterface.greater_or_equal,
    '==': MIPSInterface.equal,
    '!=': MIPSInterface.not_equal,
    '&&': MIPSInterface.logical_and,
    '||': MIPSInterface.logical_or,
    '!': MIPSInterface.logical_not,
    '++': MIPSInterface.add_immediate_unsigned,
    '--': MIPSInterface.subtract_immediate_unsigned
}
