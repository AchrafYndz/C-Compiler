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
        '''
        REGISTERS = {
            't': 10,
            's': 8,
            'a': 4,
            'v': 2,
            'f': 31
        }'''

        # start
        variable_node = node.children[1]

        self.mips_interface.enter_function(variable_node.name)

        args_nodes = [child for child in node.children if isinstance(child, FunctionArgumentNode)]
        args_nodes_count = len(args_nodes)

        store_registers = ["fp", "ra", "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7"]
        store_offset = args_nodes_count * -4

        for index, register in enumerate(store_registers):
            self.mips_interface.store_word(register1=register, offset=store_offset - (4 * index), register2="sp")

        self.mips_interface.move("fp", "sp")

        # function body code
        self.visitChildren(node)

        self.mips_interface.move("sp", "fp")

        for index, register in enumerate(reversed(store_registers)):
            self.mips_interface.load_word(
                register1=register,
                offset=store_offset - ((len(store_registers) - 1)*4 - (4 * index)),
                register2="sp"
            )

        self.mips_interface.leave_function()

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
