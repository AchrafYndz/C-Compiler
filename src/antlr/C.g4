grammar C;

/* Lexer Rules */

INCLUDE: '#include';

FILE_EXT: '.h';

INT: [0-9][0-9]*;

FLOAT: [0-9]* '.' [0-9]+;

CONST: 'const';

TYPE: 'char'| 'float' | 'int';

VOID: 'void';

IF: 'if';
ELSE: 'else';
SWITCH: 'switch';
CASE: 'case';

FOR: 'for';
WHILE: 'while';
DO: 'do';
CONTINUE: 'continue';
BREAK: 'break';
RETURN: 'return';

PRINTF: 'printf';
SCANF: 'scanf';

IDENTIFIER: START_IDENTIFIER BODY_IDENTIFIER;
fragment
START_IDENTIFIER: [a-zA-Z];
fragment
BODY_IDENTIFIER: [a-zA-Z0-9_]*;

REF: '&';

INCR: '++';
DECR: '--';

PLUS: '+';
MIN: '-';
MUL_PTR: '*';
DIV: '/';
MOD: '%';

GT: '>';
LT: '<';
EQ: '==';
GEQ: '>=';
LEQ: '<=';
NEQ: '!=';

ASS: '=';

LPARA: '(';
RPARA: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';

AND: '&&';
OR: '||';
NOT: '!';

SEMI: ';';
COLON: ':';
COMMA: ',';

DOUBLE_QUOTE: '"';

STRING: DOUBLE_QUOTE .*? DOUBLE_QUOTE;

COMMENT: (LINE_COMMENT | BLOCK_COMMENT) -> channel(2);
fragment
LINE_COMMENT: '//' ~[\r\n]*;
fragment
BLOCK_COMMENT: '/*' .*? '*/';

CHAR: '\'' CHARSEQUENCE '\'';
fragment
CHARSEQUENCE: ~['\\\r\n] | ESCAPESEQUENCE;
fragment
ESCAPESEQUENCE: '\\' ['"?abfnrtv\\];

WS: [ \n\t\r]+ -> skip;


/* Parser Rules */

program: include* (function_declaration | declaration SEMI | statement)* EOF;

include: INCLUDE LT IDENTIFIER FILE_EXT GT SEMI?;

function_declaration: (type_declaration | VOID) IDENTIFIER LPARA (function_argument (COMMA function_argument)*)? RPARA (SEMI|scope);

type_declaration: CONST? TYPE? (MUL_PTR CONST?)*;

function_argument: type_declaration IDENTIFIER;

scope: LBRACE (declaration SEMI| statement | function_declaration)* RBRACE;

declaration: type_declaration variable_definition (COMMA variable_definition)*;

variable_definition: (IDENTIFIER (LBRACK literal RBRACK)? (ASS expression)?)
                    | IDENTIFIER LBRACK RBRACK ASS LBRACE (expression (COMMA expression)*)? RBRACE;

statement: scope
           | expression SEMI
           | conditional
           | loop
           | branch;

/* https://www.tutorialspoint.com/cprogramming/c_operators_precedence.htm */
expression: (function_call|print|scan)
            | expression operation=LBRACK expression RBRACK // Postfix
            | expression operation=(INCR | DECR) // Postfix
            | LPARA operation=TYPE RPARA expression // Unary
            | operation=(PLUS | MIN | NOT | INCR | DECR | REF | MUL_PTR) expression // Unary
            | expression operation=(MUL_PTR | DIV | MOD) expression // Multiplicative
            | expression operation=(PLUS | MIN) expression // Additive
            | expression operation=(LT | LEQ | GT | GEQ) expression // Relational
            | expression operation=(EQ | NEQ) expression // Equality
            | expression operation=AND expression // Logical AND
            | expression operation=OR expression // Logical OR
            | LPARA expression RPARA
            | IDENTIFIER
            | literal;

function_call: IDENTIFIER LPARA (expression (COMMA expression)*)? RPARA;

print: PRINTF LPARA STRING (COMMA expression)* RPARA;

scan: SCANF LPARA STRING (COMMA expression)* RPARA;

literal: CHAR | STRING | INT | FLOAT;

conditional: IF LPARA expression RPARA statement (ELSE statement)?
             | SWITCH LPARA expression RPARA statement
             | CASE literal COLON statement;

loop: WHILE LPARA expression RPARA statement
      | FOR LPARA declaration? SEMI expression? SEMI expression? RPARA statement
      | DO statement WHILE LPARA expression RPARA SEMI;

branch: RETURN expression? SEMI
        | (CONTINUE|BREAK) SEMI;
