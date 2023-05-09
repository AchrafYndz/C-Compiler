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
            VariableNode: self.visitVariable
        }

    def visitChildren(self, node):
        for child in node.children:
            visit_method = self.nodes_dict[type(child)]
            print(f"Calling {visit_method}.")
            visit_method(child)

    def visitArray_assignment(self, node):
        self.visitChildren(node)

    def visitAssignment(self, node):
        self.visitChildren(node)

    def visitBinary_expression(self, node):
        self.visitChildren(node)

    def visitBranch(self, node):
        self.visitChildren(node)

    def visitConditional(self, node):
        self.visitChildren(node)

    def visitDeclaration(self, node):
        self.visitChildren(node)

    def visitExplicit_conversion(self, node):
        self.visitChildren(node)

    def visitFunction_argument(self, node):
        self.visitChildren(node)

    def visitFunction_call(self, node):
        self.visitChildren(node)

    def visitFunction(self, node):
        self.visitChildren(node)

    def visitInclude(self, node):
        self.visitChildren(node)

    def visitLiteral(self, node):
        self.visitChildren(node)

    def visitLoop(self, node):
        self.visitChildren(node)

    def visitScope(self, node):
        self.visitChildren(node)

    def visitType_declaration(self, node):
        self.visitChildren(node)

    def visitUnary_expression(self, node):
        self.visitChildren(node)

    def visitVariable_definition(self, node):
        self.visitChildren(node)

    def visitVariable(self, node):
        self.visitChildren(node)
