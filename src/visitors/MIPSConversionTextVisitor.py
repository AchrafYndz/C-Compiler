from src.MIPSInterface import MIPSInterface
from src.MIPSUtil import INSTRUCTIONS
from src.SymbolTable import SymbolTable
from src.Util import get_type, cast_to_type, extract_leaves, extract_deref
from src.ast_nodes import *
from src.visitors.ASTVisitor import ASTVisitor
import uuid


class MIPSConversionTextVisitor(ASTVisitor):
    def __init__(self, symbol_table: SymbolTable, mips_interface):
        super().__init__()
        self.symbol_table = symbol_table
        self.scope_counter: int = 1
        self.mips_interface = mips_interface
        self.current_loop_id = -1
        self.end_count = -1

    def visitArray_assignment(self, node: ArrayAssignmentNode):
        self.visitChildren(node)

        array_name = node.name
        index_register = self.mips_interface.get_free_register()
        self.mips_interface.load_immediate(index_register, node.index)
        self.mips_interface.multiply_immediate(index_register, index_register, 4)

        if isinstance(node.children[0], LiteralNode):
            value = node.children[0].value
            self.mips_interface.assign_array_element_immediate(value, array_name, index_register)
        elif isinstance(node.children[0], VariableNode):
            value_register = self.mips_interface.get_free_register()
            self.mips_interface.load_variable(value_register, node.children[0].name)
            self.mips_interface.assign_array_element(value_register, array_name, index_register)
            self.mips_interface.free_up_registers([value_register])
        else:
            value_register = self.mips_interface.last_expression_registers.pop(0)
            self.mips_interface.assign_array_element(value_register, array_name, index_register)
            self.mips_interface.free_up_registers([value_register])
        self.mips_interface.free_up_registers([index_register])

    def visitAssignment(self, node: AssignmentNode):
        self.visitChildren(node)

        # defined
        if len(node.children) == 1:
            if isinstance(node.children[0], LiteralNode):
                register = "t0"
                l_type = self.symbol_table.get_variable(node.name).type_
                self.mips_interface.load_immediate("t0", cast_to_type(l_type, node.children[0].value))
            elif isinstance(node.children[0], VariableNode):
                register = "t0"
                self.mips_interface.load_variable("t0", node.children[0].name)
            elif isinstance(node.children[0], FunctionCallNode):
                register = "t0"
                self.mips_interface.move("t0", "v1")
            else:
                register = self.mips_interface.last_expression_registers.pop(0)
            self.mips_interface.store_in_variable(node.name, register)

    def visitBinary_expression(self, node: BinaryExpressionNode):
        self.visitChildren(node)

        # get element from array
        if node.operator == "[]":
            if isinstance(node.children[1], LiteralNode):
                index = int(node.children[1].value)
                index_register = self.mips_interface.get_free_register()
                self.mips_interface.load_immediate(index_register, index*4)
            elif isinstance(node.children[1], VariableNode):
                index_register = self.mips_interface.get_free_register()
                self.mips_interface.load_variable(index_register, node.children[1].name)
                self.mips_interface.multiply_immediate(index_register, index_register, 4)
            # expression
            else:
                index_register = self.mips_interface.last_expression_registers.pop(0)
                self.mips_interface.multiply_immediate(index_register, index_register, 4)
            result_register = self.mips_interface.get_free_register()
            self.mips_interface.last_expression_registers.append(result_register)
            self.mips_interface.load_array_element(result_register, node.children[0].name, index_register)
            self.mips_interface.free_up_registers([index_register])
            return

        type_ = get_type(node, self.symbol_table)
        type_ = TypeEnum.INT if type_ == TypeEnum.CHAR else type_

        mips_instruction = INSTRUCTIONS[node.operator]
        operators = []
        visited_func_call = False
        for i, child_node in enumerate(node.children):
            if isinstance(child_node, VariableNode):
                free_register = self.mips_interface.get_free_register()
                self.mips_interface.load_variable(free_register, child_node.name)
                operators.append(free_register)
            elif isinstance(child_node, LiteralNode):
                free_register = self.mips_interface.get_free_register()
                self.mips_interface.load_immediate(free_register, cast_to_type(type_, child_node.value))
                operators.append(free_register)
            elif isinstance(child_node, FunctionCallNode):
                if not visited_func_call:
                    operators.append("v1")
                    visited_func_call = True
                else:
                    operators.append("s1")
            elif isinstance(child_node, UnaryExpressionNode) and child_node.operator in ["++", "--"]:
                var_node = child_node.children[0]

                free_register = self.mips_interface.get_free_register()
                self.mips_interface.load_variable(free_register, var_node.name)
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

    def visitBranch(self, node: BranchNode):
        self.visitChildren(node)
        if node.sort == "continue":
            self.mips_interface.jump(f"loop_{self.current_loop_id}")
        elif node.sort == "break":
            self.mips_interface.jump(f"end_{self.current_loop_id}")
        elif node.sort == "return":
            if not node.children:
                return
            if isinstance(node.children[0], VariableNode):
                value_register = self.mips_interface.get_free_register()
                self.mips_interface.load_variable(value_register, node.children[0].name)
                self.mips_interface.move("v1", value_register)
                self.mips_interface.free_up_registers([value_register])
            elif isinstance(node.children[0], LiteralNode):
                self.mips_interface.add_immediate_unsigned("v1", "zero", node.children[0].value)
            elif isinstance(node.children[0], FunctionCallNode):
                pass
            else:
                self.mips_interface.move("v1", self.mips_interface.last_expression_registers.pop(0))

    def visitConditional(self, node: ConditionalNode):
        expression_node = node.children[0]
        visit_method = self.nodes_dict[type(expression_node)]
        visit_method(expression_node)

        has_else = node.has_else

        index = uuid.uuid4().hex

        if isinstance(node.children[0], LiteralNode) and \
           node.children[0].value == "1":
                self.mips_interface.jump_and_link(f"if_{index}")
                # if
                self.mips_interface.append_label(f"if_{index}")
                if_body = node.children[1]
                visit_method = self.nodes_dict[type(if_body)]
                visit_method(if_body)
                self.mips_interface.jump(f"end_{index}")
        elif isinstance(node.children[0], LiteralNode) and \
           node.children[0].value == "0":
            pass
            if has_else:
                self.mips_interface.jump_and_link(f"else_{index}")
                # else
                self.mips_interface.append_label(f"else_{index}")
                else_body = node.children[2]
                visit_method = self.nodes_dict[type(else_body)]
                visit_method(else_body)
                self.mips_interface.jump(f"end_{index}")
            else:
                self.mips_interface.jump_and_link(f"end_{index}")
        else:
            e_reg = self.mips_interface.last_expression_registers.pop(0)
            if not has_else:
                self.mips_interface.branch_equal(e_reg, "1", f"if_{index}")
                self.mips_interface.branch_equal(e_reg, "0", f"end_{index}")
                # if
                self.mips_interface.append_label(f"if_{index}")
                if_body = node.children[1]
                visit_method = self.nodes_dict[type(if_body)]
                visit_method(if_body)
                self.mips_interface.jump(f"end_{index}")
            else:
                self.mips_interface.branch_equal(e_reg, "1", f"if_{index}")
                self.mips_interface.branch_equal(e_reg, "0", f"else_{index}")
                # if
                self.mips_interface.append_label(f"if_{index}")
                if_body = node.children[1]
                visit_method = self.nodes_dict[type(if_body)]
                visit_method(if_body)
                self.mips_interface.jump(f"end_{index}")

                #else
                self.mips_interface.append_label(f"else_{index}")
                else_body = node.children[2]
                visit_method = self.nodes_dict[type(else_body)]
                visit_method(else_body)
                self.mips_interface.jump(f"end_{index}")
            self.mips_interface.free_up_registers([e_reg])

        self.mips_interface.append_label(f"end_{index}")

    def visitDeclaration(self, node: DeclarationNode):
        self.visitChildren(node)

    def visitExplicit_conversion(self, node: ExplicitConversionNode):
        self.visitChildren(node)

    def visitFunction_argument(self, node: FunctionArgumentNode):
        self.visitChildren(node)

    def visitFunction_call(self, node: FunctionCallNode):
        self.visitChildren(node)

        if node.name == "printf":
            # printing a string
            if len(node.children) == 1:
                to_print_node = node.children[0]
                to_print = to_print_node.value.replace('"', "")
                # label = self.mips_interface.variable[to_print]
                label, _ = self.mips_interface.get_label(to_print, defined=True)
                self.mips_interface.print(label, to_print_node.type)
                return

            # can be either a variable or a literal
            to_print_nodes = node.children[1:]
            for to_print_node in to_print_nodes:
                is_variable = False
                is_expression = False
                to_print = None
                is_string = False
                type_ = None

                if isinstance(to_print_node, LiteralNode):
                    is_string = (to_print_node.type == TypeEnum.STRING)
                    to_print = to_print_node.value.replace('"', "")
                    type_ = to_print_node.type
                elif isinstance(to_print_node, VariableNode):
                    var_obj = self.symbol_table.get_variable(to_print_node.name)
                    type_ = var_obj.type_
                    if var_obj.isArray():
                        index_register = self.mips_interface.get_free_register()
                        self.mips_interface.load_immediate(index_register, 0)
                        register = self.mips_interface.get_free_register()
                        for i in range(var_obj.array_count):
                            self.mips_interface.load_array_element(register, var_obj.name, index_register)
                            self.mips_interface.print(register, type_=type_, is_expression=True)
                            # increase the index
                            self.mips_interface.add_immediate_unsigned(index_register, index_register, 4)
                        self.mips_interface.free_up_registers([index_register, register])
                        return
                    else:
                        self.mips_interface.load_variable("t0", to_print_node.name)
                        is_variable = True
                elif isinstance(to_print_node, FunctionCallNode):
                    self.mips_interface.print("v1", TypeEnum.INT, is_expression=True)
                    return
                else:
                    type_ = TypeEnum.INT
                    is_expression = True
                    to_print = self.mips_interface.last_expression_registers.pop(0)

                if is_string:
                    label = self.mips_interface.variable[to_print]
                    self.mips_interface.print(label, type_)
                else:
                    types = {
                        "%i": TypeEnum.INT,
                        "%f": TypeEnum.FLOAT,
                        "%d": TypeEnum.INT,
                        "%c": TypeEnum.CHAR,
                        "%s": TypeEnum.STRING
                    }
                    type_arg = node.children[0].value.replace('"', '')
                    to_cast_type = types[type_arg]
                    self.mips_interface.print(to_print, to_cast_type, is_variable, is_expression)

        elif node.name == "scanf":
            assert isinstance(node.children[1], UnaryExpressionNode), "scanf expected unary expression"
            arg_node = node.children[0]
            to_write_node = node.children[1].children[0]
            var_obj = self.symbol_table.get_variable(to_write_node.name)
            if var_obj.isArray():
                pass
            else:
                self.mips_interface.scan(to_write_node.name)
                self.mips_interface.last_expression_registers.pop(0)

        else:
            for i, arg in enumerate(node.children):
                if isinstance(arg, LiteralNode):
                    self.mips_interface.add_immediate_unsigned(f"a{i}", "zero", arg.value)
                elif isinstance(arg, VariableNode):
                    self.mips_interface.load_variable(f"a{i}", arg.name)
                else:
                    # expression
                    expression_register = self.mips_interface.last_expression_registers.pop(0)
                    self.mips_interface.move(f"a{i}", expression_register)
            self.mips_interface.jump_and_link(node.name)
            parent_node = node.parent
            if not isinstance(node.parent, BinaryExpressionNode):
                return
            first_child = parent_node.children[0] == node
            if not first_child:
                return
            sibling = parent_node.children[1]
            if not isinstance(sibling, FunctionCallNode):
                return

            # fib(i-1) + fib(i-2)
            self.mips_interface.move("s1", "v1")

    def visitFunction(self, node: FunctionNode):
        # start
        variable_node = node.children[1]
        has_body = False

        for child in node.children:
            if isinstance(child, ScopeNode):
                has_body = True

        # overslaan van lege functies - handig voor forward declr
        if not has_body:
            return

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
        #self.end_count += 1
        #self.current_loop_id = self.end_count

        index = uuid.uuid4().hex
        self.current_loop_id = index
        
        self.mips_interface.append_label(f"loop_{index}")
        # body
        loop_body = node.children[1]
        visit_method = self.nodes_dict[type(loop_body)]
        visit_method(loop_body)

        # expr
        expression_node = node.children[0]
        visit_method = self.nodes_dict[type(expression_node)]
        visit_method(expression_node)
        # expr_reg = self.mips_interface.last_expression_registers.pop()
        expr_reg = self.mips_interface.last_expression_registers.pop(0)

        self.mips_interface.branch_equal(expr_reg, "1", f"loop_{index}")
        self.mips_interface.jump(f"end_{index}")

        self.mips_interface.free_up_registers([expr_reg])

        self.mips_interface.append_label(f"end_{index}")

        #self.end_count -= 1
        #self.current_loop_id = i

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
                # ++, --
                mips_instruction(
                    self.mips_interface,
                    result_register,
                    register,
                    "1"
                )
                if isinstance(child_node, VariableNode):
                    self.mips_interface.store_in_variable(child_node.name, result_register)
                elif isinstance(child_node, UnaryExpressionNode) and child_node.operator == "*":
                    var_node = child_node.children[0]
                    assert isinstance(var_node, VariableNode), "Dereference of non variable"
                    self.mips_interface.store_in_variable(var_node.name, result_register)
                else:
                    raise ValueError(f"Expected {node.operator} of variable or *variable")
                self.mips_interface.last_expression_registers.pop(0)
            self.mips_interface.free_up_registers([register])

        elif node.operator == "&":
            register = self.mips_interface.get_free_register()
            var_obj = self.symbol_table.get_variable(child_node.name, expected=True)
            if var_obj.isArray():
                self.mips_interface.scan_array(var_obj.name, var_obj.array_count, var_obj.type_)
            else:
                offset = self.mips_interface.local_variables[child_node.name]
                self.mips_interface.load_address(register, f"{offset}($sp)")
            self.mips_interface.last_expression_registers.append(register)

        elif node.operator == "*":
            if isinstance(node.parent, UnaryExpressionNode) and node.parent.operator == "*":
                return
            register = self.mips_interface.get_free_register()
            var_name, ptr_level = extract_deref(node)
            # get number of star operators
            self.mips_interface.load_variable(register, var_name)
            for _ in range(ptr_level):
                self.mips_interface.load_word(register, 0, register)
            self.mips_interface.last_expression_registers.append(register)

        else:
            raise ValueError("Expected unary expression to have operator ++, --, &, * or !")

    def visitVariable_definition(self, node: VariableDefinitionNode):
        self.visitChildren(node)

        # global variable
        if self.symbol_table.current_scope.name == "1":
            value_node: LiteralNode = node.children[0]
            self.mips_interface.append_global_variable(node.name, value_node.value, node.type)
            return

        # undefined array
        if node.is_array and len(node.children) == 1:
            return

        # defined array
        if node.is_array and len(node.children) > 1:
            self.mips_interface.define_array(node.name, node.children)
            return

        # defined variable
        if node.children:
            if isinstance(node.children[0], LiteralNode):
                register = self.mips_interface.get_free_register()
                self.mips_interface.load_immediate(register, cast_to_type(node.type.type, node.children[0].value))
            elif isinstance(node.children[0], VariableNode):
                register = self.mips_interface.get_free_register()
                self.mips_interface.load_variable(register, node.children[0].name)
            elif isinstance(node.children[0], FunctionCallNode):
                register = self.mips_interface.get_free_register()
                self.mips_interface.move(register, "v1")
            else:
                register = self.mips_interface.last_expression_registers.pop(0)
        # undefined variable
        else:
            register = self.mips_interface.get_free_register()
            self.mips_interface.load_immediate(register, 0)

        self.mips_interface.append_variable(register, node.name)
        self.mips_interface.free_up_registers([register])

    def visitVariable(self, node: VariableNode):
        self.visitChildren(node)
        
    def visitComment(self, node: CommentNode):
        self.visitChildren(node)
        lines = node.content.splitlines()
        lines_with_hashtags = ['#' + line for line in lines]
        result = '\n'.join(lines_with_hashtags)
        self.mips_interface.append_instruction(f"{result}")
