from src.SymbolTable import SymbolTable
from src.ast_nodes import *
from src.visitors.ASTVisitor import ASTVisitor
from src.MIPSInterface import MIPSInterface


class MIPSConversionVisitor(ASTVisitor):
    def __init__(self, symbol_table: SymbolTable):
        super().__init__()
        self.symbol_table = symbol_table
        self.scope_counter: int = 1
        self.mips_interface = MIPSInterface()

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

        if variable_node.name == "main":
            self.mips_interface.jump_and_link("main")
            self.mips_interface.exit()

        self.mips_interface.enter_function(variable_node.name)

        # self.mips_interface.append_instruction("addiu $sp, $sp, -16")
        # self.mips_interface.append_instruction("sw $ra, 12($sp)")
        # self.mips_interface.append_instruction("sw $fp, 8($sp)")
        # self.mips_interface.append_instruction("move $fp, $sp")
        # self.mips_interface.append_instruction("sw $zero, 4($fp)")

        # function body here
        # self.mips_interface.append_instruction("addiu $2, $zero, 0")  # saving of return value
        self.visitChildren(node)

        # end
        self.mips_interface.leave_function()
        # self.mips_interface.append_instruction("move $sp, $fp")
        # self.mips_interface.append_instruction("lw $fp, 8($sp)")
        # self.mips_interface.append_instruction("lw $ra, 12($sp)")
        # self.mips_interface.append_instruction("addiu $sp, $sp, 16")
        #
        # self.mips_interface.append_instruction("jr $ra")
        # self.mips_interface.append_instruction("nop")

    def visitInclude(self, node: IncludeNode):
        self.visitChildren(node)

    def visitLiteral(self, node: LiteralNode):
        if node.type == TypeEnum.STRING:
            self.mips_interface.append_string(node.value)
        self.visitChildren(node)

    def visitLoop(self, node: LoopNode):
        self.visitChildren(node)

    def visitScope(self, node: ScopeNode):
        scope_to_enter = self.symbol_table.get_scope(str(self.scope_counter))
        self.scope_counter += 1

        self.symbol_table.enter_scope(scope_to_enter)
        self.visitChildren(node)
        self.symbol_table.leave_scope()

    def visitType_declaration(self, node: TypeDeclarationNode):
        self.visitChildren(node)

    def visitUnary_expression(self, node: UnaryExpressionNode):
        self.visitChildren(node)

    def visitVariable_definition(self, node: VariableDefinitionNode):
        # global variable
        if self.symbol_table.current_scope.name == "1":
            value_node: LiteralNode = node.children[0]
            self.mips_interface.append_global_variable(node.name, value_node.value, node.type)

        self.visitChildren(node)

    def visitVariable(self, node: VariableNode):
        self.visitChildren(node)
