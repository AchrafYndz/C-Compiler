from src.MIPSUtil import INSTRUCTIONS
from src.SymbolTable import SymbolTable
from src.Util import get_type
from src.ast_nodes import *
from src.visitors.ASTVisitor import ASTVisitor


class MIPSConversionTextVisitor(ASTVisitor):
    def __init__(self, symbol_table: SymbolTable, mips_interface):
        super().__init__()
        self.symbol_table = symbol_table
        self.scope_counter: int = 1
        self.mips_interface = mips_interface

    def visitArray_assignment(self, node: ArrayAssignmentNode):
        self.visitChildren(node)

    def visitAssignment(self, node: AssignmentNode):
        if len(node.children) == 1:
            if isinstance(node.children[0], LiteralNode):
                self.mips_interface.load_immediate("t0", node.children[0].value)
            elif isinstance(node.children[0], VariableNode):
                self.mips_interface.load_variable("t0", node.children[0].name)
            elif isinstance(node.children[0], FunctionCallNode):
                self.mips_interface.move("t0", "v0")
        self.mips_interface.store_in_variable(node.name)

        self.visitChildren(node)

    def visitBinary_expression(self, node: BinaryExpressionNode):
        self.visitChildren(node)

        type_ = get_type(node, self.symbol_table)
        type_ = TypeEnum.INT if type_ == TypeEnum.CHAR else type_

        mips_instruction = INSTRUCTIONS[node.operator]
        operators = []
        for i, child_node in enumerate(node.children):
            if isinstance(child_node, VariableNode):
                free_register = self.mips_interface.get_free_register()
                self.mips_interface.load_variable(free_register, child_node.name)
                operators.append(free_register)
            elif isinstance(child_node, LiteralNode):
                free_register = self.mips_interface.get_free_register()
                self.mips_interface.load_immediate(free_register, child_node.value)
                operators.append(free_register)
            else:
                expression_register = self.mips_interface.last_expression_registers.pop(0)
                operators.append(expression_register)

        result_register = self.mips_interface.get_free_register()
        self.mips_interface.last_expression_registers.append(result_register)

        mips_instruction(
            self.mips_interface,
            result_register,
            operators[0],
            operators[1]
        )
        self.mips_interface.free_up_registers(operators)

        print(self.mips_interface.last_expression_registers)

    def visitBranch(self, node: BranchNode):
        self.visitChildren(node)
        if node.sort == "return":
            self.mips_interface.move("v0", self.mips_interface.last_expression_registers.pop(0))

    def visitConditional(self, node: ConditionalNode):
        self.visitChildren(node)

    def visitDeclaration(self, node: DeclarationNode):
        self.visitChildren(node)

    def visitExplicit_conversion(self, node: ExplicitConversionNode):
        self.visitChildren(node)

    def visitFunction_argument(self, node: FunctionArgumentNode):
        self.visitChildren(node)

    def visitFunction_call(self, node: FunctionCallNode):
        if node.name == "printf":
            if len(node.children) == 1:
                # must be a string
                to_print_node = node.children[0]
                to_print = to_print_node.value.replace('"', "")
                label = self.mips_interface.data[to_print]
                self.mips_interface.print(label, to_print_node.type)
            else:
                # can be either a variable or a literal
                to_print_nodes = node.children[1:]
                for to_print_node in to_print_nodes:
                    is_variable = False
                    to_print = None
                    is_string = False
                    type_ = None

                    if isinstance(to_print_node, LiteralNode):
                        is_string = (to_print_node.type == TypeEnum.STRING)
                        to_print = to_print_node.value.replace('"', "")
                        type_ = to_print_node.type
                    elif isinstance(to_print_node, VariableNode):
                        self.mips_interface.load_variable("t0", to_print_node.name)
                        var_obj = self.symbol_table.get_variable(to_print_node.name)
                        type_ = var_obj.type_
                        is_variable = True
                    if is_string:
                        label = self.mips_interface.data[to_print]
                        self.mips_interface.print(label, type_)
                    else:
                        self.mips_interface.print(to_print, type_, is_variable)
        else:
            for i, arg in enumerate(node.children):
                if isinstance(arg, LiteralNode):
                    self.mips_interface.add_immediate_unsigned(f"a{i}", "zero", arg.value)
            self.mips_interface.jump_and_link(node.name)
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
        self.mips_interface.subtract_immediate_unsigned("sp", "sp", (len(store_registers)+1) * 4)

        for i, arg_node in enumerate(args_nodes):
            self.mips_interface.append_variable(f"a{i}", arg_node.name)

        # function body code
        self.visitChildren(node)

        self.mips_interface.add_immediate_unsigned("sp", "sp", (len(store_registers)+1) * 4)
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
        # ++, --, &, *, !
        child_node = node.children[0]
        if node.operator in ["!", "++", "--"]:
            mips_instruction = INSTRUCTIONS[node.operator]

            if isinstance(child_node, VariableNode):
                register = self.mips_interface.get_free_register()
                self.mips_interface.load_variable(register, child_node.name)
            else:
                register = self.mips_interface.last_expression_registers.pop(0)

            result_register = self.mips_interface.get_free_register()
            self.mips_interface.last_expression_registers.append(result_register)

            if node.operator == "!":
                mips_instruction(
                    self.mips_interface,
                    result_register,
                    register
                )
            else:
                mips_instruction(
                    self.mips_interface,
                    result_register,
                    register,
                    "1"
                )
                self.mips_interface.store_in_variable(child_node.name, result_register)
            self.mips_interface.free_up_registers([register])

        elif node.operator == "&":
            register = self.mips_interface.get_free_register()
            offset = self.mips_interface.local_variables[child_node.name]
            self.mips_interface.load_address(register, f"{offset}($sp)")
            self.mips_interface.last_expression_registers.append(register)

        elif node.operator == "*":
            register = self.mips_interface.get_free_register()
            self.mips_interface.load_variable(register, child_node.name)
            self.mips_interface.load_word(register, 0, register)
            self.mips_interface.last_expression_registers.append(register)

        else:
            raise ValueError("Expected unary expression to have operator ++, --, &, * or !")

        self.visitChildren(node)

    def visitVariable_definition(self, node: VariableDefinitionNode):
        self.visitChildren(node)

        if self.symbol_table.current_scope.name == "1":
            # global variable
            value_node: LiteralNode = node.children[0]
            self.mips_interface.append_global_variable(node.name, value_node.value, node.type)
        else:
            register = None
            # local variable
            if isinstance(node.children[0], LiteralNode):
                register = self.mips_interface.get_free_register()
                self.mips_interface.load_immediate(register, node.children[0].value)
            elif isinstance(node.children[0], VariableNode):
                register = self.mips_interface.get_free_register()
                self.mips_interface.load_variable(register, node.children[0].name)
            elif isinstance(node.children[0], FunctionCallNode):
                register = self.mips_interface.get_free_register()
                self.mips_interface.move(register, "v0")
            else:
                register = self.mips_interface.last_expression_registers.pop(0)
            self.mips_interface.append_variable(register, node.name)
            self.mips_interface.free_up_registers([register])

    def visitVariable(self, node: VariableNode):
        self.visitChildren(node)
