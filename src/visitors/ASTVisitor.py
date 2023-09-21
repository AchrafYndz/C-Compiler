from src.ast_nodes import *


class ASTVisitor:
    def __init__(self):
        self.nodes_dict = {
            ArrayAssignmentNode: self.visitArray_assignment,
            AssignmentNode: self.visitAssignment,
            BinaryExpressionNode: self.visitBinary_expression,
            BranchNode: self.visitBranch,
            ConditionalNode: self.visitConditional,
            DeclarationNode: self.visitDeclaration,
            ExplicitConversionNode: self.visitExplicit_conversion,
            FunctionArgumentNode: self.visitFunction_argument,
            FunctionCallNode: self.visitFunction_call,
            FunctionNode: self.visitFunction,
            IncludeNode: self.visitInclude,
            LiteralNode: self.visitLiteral,
            LoopNode: self.visitLoop,
            ScopeNode: self.visitScope,
            TypeDeclarationNode: self.visitType_declaration,
            UnaryExpressionNode: self.visitUnary_expression,
            VariableDefinitionNode: self.visitVariable_definition,
            VariableNode: self.visitVariable,
            CommentNode: self.visitComment
        }

    def visitChildren(self, node):
        for child in node.children:
            visit_method = self.nodes_dict[type(child)]
            visit_method(child)

    def visitArray_assignment(self, node: ArrayAssignmentNode):
        self.visitChildren(node)

    def visitAssignment(self, node: AssignmentNode):
        self.visitChildren(node)

    def visitBinary_expression(self, node: BinaryExpressionNode):
        self.visitChildren(node)

    def visitBranch(self, node: BranchNode):
        self.visitChildren(node)

    def visitConditional(self, node: ConditionalNode):
        self.visitChildren(node)

    def visitDeclaration(self, node: DeclarationNode):
        self.visitChildren(node)

    def visitExplicit_conversion(self, node: ExplicitConversionNode):
        self.visitChildren(node)

    def visitFunction_argument(self, node: FunctionArgumentNode):
        self.visitChildren(node)

    def visitFunction_call(self, node: FunctionCallNode):
        self.visitChildren(node)

    def visitFunction(self, node: FunctionNode):
        self.visitChildren(node)

    def visitInclude(self, node: IncludeNode):
        self.visitChildren(node)

    def visitLiteral(self, node: LiteralNode):
        self.visitChildren(node)

    def visitLoop(self, node: LoopNode):
        self.visitChildren(node)

    def visitScope(self, node: ScopeNode):
        self.visitChildren(node)

    def visitType_declaration(self, node: TypeDeclarationNode):
        self.visitChildren(node)

    def visitUnary_expression(self, node: UnaryExpressionNode):
        self.visitChildren(node)

    def visitVariable_definition(self, node: VariableDefinitionNode):
        self.visitChildren(node)

    def visitVariable(self, node: VariableNode):
        self.visitChildren(node)
        
    def visitComment(self, node: CommentNode):
        self.visitChildren(node)
