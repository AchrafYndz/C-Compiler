from src.Type import TypeEnum

INSTRUCTIONS = {
    TypeEnum.INT: {
        '+': 'add',
        '-': 'sub',
        '*': 'mul',
        '/': 'div',
        '%': 'rem',
        '<': 'slt',
        '>': 'sgt',
        '<=': 'sle',
        '>=': 'sge',
        '==': 'seq',
        '!=': 'sne',
        '&&': 'and',
        '||': 'or'
    },
    TypeEnum.FLOAT: {
        '+': 'add.s',
        '-': 'sub.s',
        '*': 'mul.s',
        '/': 'div.s',
        '<': 'slt',
        '>': 'sgt',
        '<=': 'sle',
        '>=': 'sge',
        '==': 'seq',
        '!=': 'sne',
        '&&': 'and',
        '||': 'or'
    }
}