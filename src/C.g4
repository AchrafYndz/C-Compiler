grammar C;

/* Lexer Rules */

INCLUDE: '#include <stdio.h>' SEMI?;

INT: [0-9][0-9]*;

FLOAT: [0-9]* '.' [0-9]+;

CONST: 'const';

TYPE: 'char'| 'float' | 'int';

VOID: 'void';

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

COMMENT: LINE_COMMENT | BLOCK_COMMENT;
fragment
LINE_COMMENT: '//' ~[\r\n]*;
fragment
BLOCK_COMMENT: '/*' .*? '*/';

CHAR: '\'' CHARSEQUENCE '\'';
fragment
CHARSEQUENCE: ~['\\\r\n] | ESCAPESEQUENCE;
fragment
ESCAPESEQUENCE: '\\' ['"?abfnrtv\\];


/* Parser Rules */

program: include? (function_declaration (SEMI | scope) /* | declaration SEMICOLON*/)* EOF;

include: INCLUDE;

function_declaration: function_return_type IDENTIFIER LPARA (function_argument (COMMA function_argument)*)? RPARA;

function_argument: argument_type IDENTIFIER;

argument_type: CONST? TYPE (MUL_PTR CONST?)*;

function_return_type: (CONST? TYPE (MUL_PTR CONST?)*) | VOID;

scope: LBRACE (statement /* | declaration SEMI */)* RBRACE;

statement: scope | expression SEMI /* if statement, while and return/break/continue */;

/* https://www.tutorialspoint.com/cprogramming/c_operators_precedence.htm */
expression: function_call
            | expression operation=LBRACK expression RBRACK // Postfix
            | expression operation=(INCR | DECR) // Postfix
            | LPARA TYPE RPARA expression // Unary
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

function_call: 'pass';

literal: INT | FLOAT | CHAR;