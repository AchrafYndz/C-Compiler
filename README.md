# C-Compiler
*optional

**our own additions

- [x] Grammar
    -  [x] Binary operators
        - [x] `+`, `-` , `*` and `/`
        - [x] `%`*
    -  [x] Unary Operators: `+` and `-`
    -  [x] Relational operators
        - [x] `>`, `<` and `==`
        - [x] `>=` , `<=` and `!=`*
    -  [x] Logical operators `&&` , `||` , and `!`
    -  [x] Brackets to overwrite the order of operations
    -  [x] Types
        - [x] char
        - [x] int
        - [x] float
        - [x] pointer
    - [x] Identifiers
    - [x] Pointer Operations: `*` and `&`
    - [x] Identifier Operations: `++` and `--`*
    - [x] Definitions
    - [x] Declarations
    - [x] Implicit Conversions
    - [x] Explicit Conversions*
    - [x] Comments
    - [x] printf() for char, int & float
    - [x] Conditional Statements: `if` and `else`
    - [x] Loops: `while`, `for`, `break`, `continue`
    - [x] Unnamed Scopes
    - [x] Switch Statements: `switch`, `case`, `break`, `default`*
    - [x] Function Scopes
    - [x] Local and Global variables
    - [x] Functions
    - [x] Function Definitions
    - [x] Function Calls
    - [x] Arguments
    - [x] Return Keyword
    - [x] Void Functions
    - [x] Arrays
    - [x] Include `stdio.h`
    - [ ] Multidimensional arrays*
    - [ ] Assignments of Array rows/complete arrays in case of multidimensional arrays*
    - [ ] Dynamic arrays*

- [x] AST
  - [x] Constant folding
  - [x] Constant Propagation
  - [ ] Convert for-loops to while-loops
  - [ ] Convert switch statements to if-statements*
  - [ ] Optimizations
    - [ ] Do not generate code for statements after `return`
    - [ ] Do not generate code for statements after `break` or `continue`
    - [ ] Do not generate code for unused variables*
    - [ ] Do not generate code for conditionals that are always false*  

- [x] Error Analysis
    - [x] Syntax Errors
    - [x] Semantic Errors
      - [x] Use of an undefined or uninitialized variable.
      - [x] Redeclaration or redefinition of an existing variable.
      - [x] Operations or assignments of incompatible types.
      - [x] Assignment to an rvalue.
      - [x] Assignment to a const variable.
      - [x] Implicit Conversions warning*
      - [ ] Semantic Analysis visitor should support scoping
      - [ ] Semantic Analysis visitor should support function scopes
      - [ ] Consistency return statement with return type of function
      - [ ] Consistency forward declaration and function definition
      - [ ] For non-void functions, check that in all cases it ends with a return statement*
        
- [ ] Mips
    - [x] Binary operations + , - , * , and /
    - [x] Binary operations > , < , and ==
    - [x] Unary operators + and -
    - [x] Identifier Operations ++ and --
    - [x] Comparison operators >= , <= , and !=
    - [x] Logical operators && , || , and !
    - [x] Binary operator %
    - [x] Printf
    - [x] Pointers + pointer operators
    - [x] Local and Global variables
    - [ ] Conversions (bool <> char <> int <> float)
    - [ ] Function Scopes
    - [ ] Functions
    - [ ] Function Definitions
    - [ ] Function Calls
    - [ ] Arguments
    - [ ] Return Keyword
    - [ ] Void Functions
    - [ ] Arrays
    - [ ] Multidimensional arrays*
    - [ ] Assignments of Array rows/complete arrays in case of multidimensional arrays*
    - [ ] Dynamic arrays*
    - [ ] Include `stdio.h`
    - [ ] Conditional Statements: `if` and `else`
    - [ ] Loops: `while`, `for`, `break`, `continue`
    - [ ] Unnamed Scopes
    - [ ] Switch Statements: `switch`, `case`, `break`, `default`
    - [ ] Include comments in compiled MIPS*
    - [ ] C code comments for each instruction*
