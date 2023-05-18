from src.ast_nodes import *
from src.visitors.ASTVisitor import ASTVisitor


class MIPSConversionVisitor(ASTVisitor):

    def __init__(self):
        super().__init__()

        self.content = []
        self.local_vars = {}
        self.global_vars = {}

        # self.symbol_table = None TODO pass this

    def write_to_file(self, fileName):
        pass

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
        # start
        variable_node = node.children[1]
        self.content.append(variable_node.name + ":\n")

        self.content.append("addiu $sp, $sp, -16\n")
        self.content.append("$ra, 12($sp)")
        self.content.append("sw $fp, 8($sp)\n")
        self.content.append("move $fp, $sp\n")
        self.content.append("sw $zero, 4($fp)\n")

        # function body here
        self.content.append("addiu $2, $zero, 0\n")  # saving of return value
        self.visitChildren(node)

        # end
        self.content.append("move $sp, $fp\n")
        self.content.append("lw $fp, 8($sp)\n")
        self.content.append("lw $ra, 12($sp)\n")
        self.content.append("addiu $sp, $sp, 16\n")

        self.content.append("jr $ra\n")
        self.content.append("nop\n")

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


class MIPSFunctions:
    def __init__(self):
        self.content = []

    def addLabel(self, name, content):
        self.content.append(name + ":\n")
        # add content here

    def addReturn(self):
        pass
