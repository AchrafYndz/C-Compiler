from src.antlr.CParser import CParser
from src.antlr.CListener import CListener
from src.ast_nodes import *
from src.Type import TypeEnum, Type
from src.Util import auto_cast


class ASTCreator(CListener):
    def __init__(self):
        self.root: ASTNode = ScopeNode()
        self.current_node: ASTNode = self.root

    def enterExpression(self, ctx: CParser.ExpressionContext):
        has_operation = ctx.operation
        if not has_operation:
            # function_call, identifier or literal
            if ctx.IDENTIFIER():
                node = VariableNode(
                    name=ctx.IDENTIFIER().getText()
                )
                self.current_node.addChild(node)
            return
        operation = ctx.operation.text
        # unary expression
        if ctx.getChildCount() == 2:
            match operation:
                case "++" | "--":
                    if ctx.getText()[0:2] in ["++", "--"]:
                        node = UnaryExpressionNode(
                            operator=operation
                        )
                    else:
                        node = UnaryExpressionNode(
                            operator=operation,
                            postfix=True
                        )
                case _:
                    node = UnaryExpressionNode(
                        operator=operation
                    )
        else:
            match operation:
                case "[":
                    # array indexing
                    node = BinaryExpressionNode(
                        operator=operation + "]"
                    )
                case "char" | "int" | "float":
                    # explicit conversion
                    if operation == "int":
                        type_ = TypeEnum.INT
                    elif operation == 'float':
                        type_ = TypeEnum.FLOAT
                    elif operation == 'char':
                        type_ = TypeEnum.CHAR
                    node = ExplicitConversionNode(
                        to_type=type_
                    )
                case _:
                    # "*" | "/" | "%" | "+" | "-" | "<" | "<=" | ">" | ">=" | "==" | "!=" | "&&" | "||"
                    node = BinaryExpressionNode(
                        operator=operation
                    )
        self.current_node.addChild(node)
        self.current_node = node

    def exitExpression(self, ctx: CParser.ExpressionContext):
        if ctx.operation:
            self.current_node = self.current_node.parent

    def enterLiteral(self, ctx: CParser.LiteralContext):
        if ctx.CHAR():
            raw_value = ctx.CHAR().getText()
            escaped_char = len(raw_value) == 4
            if escaped_char:
                value = str(ord(raw_value[1:3]))
            else:
                value = str(ord(raw_value[1]))
            node = LiteralNode(
                value=value,
                type_=TypeEnum.CHAR
            )
        elif ctx.STRING():
            raw_value = ctx.STRING().getText()
            value = raw_value[1:-1]
            node = LiteralNode(
                value=value,
                type_=TypeEnum.STRING
            )
        elif ctx.INT():
            node = LiteralNode(
                value=ctx.INT().getText(),
                type_=TypeEnum.INT
            )
        elif ctx.FLOAT():
            node = LiteralNode(
                value=ctx.FLOAT().getText(),
                type_=TypeEnum.FLOAT
            )
        else:
            raise ValueError("Expected literal CHAR, STRING, INT or FLOAT.")

        self.current_node.addChild(node)

    def enterDeclaration(self, ctx: CParser.DeclarationContext):
        node = DeclarationNode()
        self.current_node.addChild(node)
        self.current_node = node

    def exitDeclaration(self, ctx: CParser.DeclarationContext):
        self.current_node = self.current_node.parent

    def enterFunction_declaration(self, ctx: CParser.Function_declarationContext):
        node = FunctionNode()
        if ctx.VOID():
            node.addChild(
                TypeDeclarationNode(
                    type_=Type(TypeEnum.VOID)
                )
            )
        node.addChild(VariableNode(ctx.IDENTIFIER().getText()))
        self.current_node.addChild(node)
        self.current_node = node

    def exitFunction_declaration(self, ctx: CParser.Function_declarationContext):
        if not isinstance(self.current_node.children[0], TypeDeclarationNode):
            self.current_node.children[0], self.current_node.children[1] = \
                self.current_node.children[1], self.current_node.children[0]

        self.current_node = self.current_node.parent

    def enterType_declaration(self, ctx: CParser.Type_declarationContext):
        children = [child.getText() for child in ctx.getChildren()]

        if 'int' in children:
            type_ = TypeEnum.INT
        elif 'float' in children:
            type_ = TypeEnum.FLOAT
        elif 'char' in children:
            type_ = TypeEnum.CHAR
        else:
            type_ = None
            # raise ValueError("Expected type CHAR, INT or FLOAT.")

        type_obj = Type(type_)
        if ctx.CONST():
            type_obj.is_const = True
        type_obj.pointer_level = len(ctx.MUL_PTR())

        node = TypeDeclarationNode(type_obj)

        self.current_node.addChild(node)
        self.current_node = node

    def exitType_declaration(self, ctx: CParser.Type_declarationContext):
        self.current_node = self.current_node.parent

    def enterVariable_definition(self, ctx: CParser.Variable_definitionContext):
        name = ctx.IDENTIFIER().getText()
        type_declaration_node = self.current_node.children[0]

        is_array = ctx.LBRACK()
        has_array_size = not ctx.LBRACE()

        if type_declaration_node.type.type:
            type_ = type_declaration_node.type

            node = VariableDefinitionNode(
                name=name,
                type_=type_,
                is_array=is_array,
                has_array_size=has_array_size
            )
        else:
            if is_array:
                array_index_node = ctx.literal().children[0]

                array_index = auto_cast(array_index_node.getText())

                node = ArrayAssignmentNode(
                    name=name,
                    index=array_index
                )
            elif len(ctx.children) == 1:
                node = VariableNode(
                    name=name
                )
            else:
                node = AssignmentNode(name)

        self.current_node.children.remove(type_declaration_node)

        self.current_node.addChild(node)
        self.current_node = node

    def exitVariable_definition(self, ctx: CParser.Variable_definitionContext):
        if isinstance(self.current_node, ArrayAssignmentNode):
            array_index_literal = self.current_node.children[0]
            self.current_node.children.remove(array_index_literal)  # remove literal for array index as child
        self.current_node = self.current_node.parent

    def enterScope(self, ctx: CParser.ScopeContext):
        node = ScopeNode()
        self.current_node.addChild(node)
        self.current_node = node

    def exitScope(self, ctx: CParser.ScopeContext):
        self.current_node = self.current_node.parent

    def enterConditional(self, ctx: CParser.ConditionalContext):
        node = ConditionalNode(has_else=not(ctx.ELSE() is None))
        self.current_node.addChild(node)
        self.current_node = node

    def exitConditional(self, ctx: CParser.ConditionalContext):
        self.current_node = self.current_node.parent

    def enterLoop(self, ctx: CParser.LoopContext):
        do_while = bool(ctx.DO())
        node = LoopNode(do_while)
        self.current_node.addChild(node)
        self.current_node = node

    def exitLoop(self, ctx: CParser.LoopContext):
        self.current_node = self.current_node.parent

    def enterBranch(self, ctx: CParser.BranchContext):
        if ctx.RETURN():
            sort = 'return'
        elif ctx.CONTINUE():
            sort = 'continue'
        elif ctx.BREAK:
            sort = 'break'
        else:
            raise ValueError("Expected branch of sort RETURN, CONTINUE or BREAK.")
        node = BranchNode(sort)
        self.current_node.addChild(node)
        self.current_node = node

    def exitBranch(self, ctx: CParser.BranchContext):
        self.current_node = self.current_node.parent

    def enterFunction_argument(self, ctx: CParser.Function_argumentContext):
        name = ctx.IDENTIFIER().getText()
        node = FunctionArgumentNode(None, name)
        self.current_node.addChild(node)
        self.current_node = node

    def exitFunction_argument(self, ctx: CParser.Function_argumentContext):
        type_declaration_node = self.current_node.children[0]
        type_ = type_declaration_node.type
        self.current_node.type = type_
        self.current_node.children.remove(type_declaration_node)

        self.current_node = self.current_node.parent

    def enterFunction_call(self, ctx: CParser.Function_callContext):
        name = ctx.IDENTIFIER().getText()
        node = FunctionCallNode(name)
        self.current_node.addChild(node)
        self.current_node = node

    def exitFunction_call(self, ctx: CParser.Function_callContext):
        self.current_node = self.current_node.parent

    def enterPrint(self, ctx: CParser.PrintContext):
        node = FunctionCallNode("printf")
        if ctx.STRING():
            node.addChild(LiteralNode(ctx.STRING().getText(), TypeEnum.STRING))
        self.current_node.addChild(node)
        self.current_node = node

    def exitPrint(self, ctx: CParser.PrintContext):
        self.current_node = self.current_node.parent

    def enterScan(self, ctx: CParser.ScanContext):
        node = FunctionCallNode("scanf")
        if ctx.STRING():
            node.addChild(LiteralNode(ctx.STRING().getText(), TypeEnum.STRING))
        self.current_node.addChild(node)
        self.current_node = node

    def exitScan(self, ctx: CParser.ScanContext):
        self.current_node = self.current_node.parent

    def enterInclude(self, ctx: CParser.IncludeContext):
        to_include = ctx.IDENTIFIER().getText() + ctx.FILE_EXT().getText()
        node = IncludeNode(to_include)
        self.current_node.addChild(node)
    
    def enterComment(self, ctx:CParser.CommentContext):
        node = CommentNode(ctx.COMMENT().getText())
        self.current_node.addChild(node)
