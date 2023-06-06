from src.SymbolTable import *
from src.visitors.ASTVisitor import *
from src.Util import auto_cast, returns_something, has_duplicates, look_in_parent, extract_print_types, \
    extract_scan_types, extract_leaves, get_type
from src.Type import TypeEnum
from src.Logger import Logger


class SemanticAnalysisVisitor(ASTVisitor):
    def __init__(self):
        super().__init__()
        self.symbol_table: SymbolTable = SymbolTable()
        self.found_main = False

    def check_is_defined(self, nodes, expression_type):
        for node in nodes:
            if isinstance(node, VariableNode):
                var_name = node.name
                var_obj = self.symbol_table.get_variable(var_name)
                if not var_obj.is_assigned:
                    Logger.get_instance().log_error(f"Undefined variable {var_name} cannot be used in {expression_type}")

    def check_not_const(self, node):
        var_name = node.name
        var_obj = self.symbol_table.get_variable(var_name)
        if var_obj.is_const:
            Logger.get_instance().log_error(f"Const variable `{var_name}` cannot be modified")

    def visitArray_assignment(self, node: ArrayAssignmentNode):
        if not isinstance(node.index, int):
            Logger.get_instance().log_error("The index of an array must be an integer.")

        # Array Access Type Mismatch
        array_obj = self.symbol_table.get_variable(node.name)
        if not isinstance(array_obj, Array):
            Logger.get_instance().log_error(f"Invalid array access usage on variable of type {array_obj.type_.name}")
        self.visitChildren(node)

    def visitAssignment(self, node: AssignmentNode):
        self.check_not_const(node)

        assignee = node.children[0]
        self.check_is_defined([assignee], "assignment")
        if isinstance(assignee, FunctionCallNode):
            function_obj = self.symbol_table.get_variable(assignee.name)
            assigned_obj = self.symbol_table.get_variable(node.name)
            if function_obj.type_ == TypeEnum.VOID:
                Logger.get_instance().log_error(
                    f"Incompatible assignment from type {function_obj.type_.name} to {assigned_obj.type_.name}")

        # check if variable is declared
        self.symbol_table.get_variable(node.name, expected=True)
        self.symbol_table.alter_identifier(node.name, is_assigned=True)

        self.visitChildren(node)

    def visitBinary_expression(self, node: BinaryExpressionNode):
        if node.operator == "[]":
            index_node = node.children[1]
            if isinstance(index_node, LiteralNode):
                if not isinstance(auto_cast(index_node.value), int):
                    Logger.get_instance().log_error("The index of an array must be an integer.")
        leaves = []
        extract_leaves(node, leaves)
        # Binary operation between 2 or more pointers
        if node.operator in ["+", "-", "*", "/", "%"]:
            pointer_vars = 0
            for leaf in leaves:
                if isinstance(leaf, VariableNode):
                    var_name = leaf.name
                    var_obj = self.symbol_table.get_variable(var_name)
                    if var_obj.ptr_level > 0:
                        pointer_vars += 1
            if pointer_vars >= 2:
                Logger.get_instance().log_error(f"Invalid operands to binary `{node.operator}` between {pointer_vars} pointers.")
        # Binary operation with at least one array
        if node.operator != "[]":
            for leaf in leaves:
                if isinstance(leaf, VariableNode):
                    var_name = leaf.name
                    var_obj = self.symbol_table.get_variable(var_name)
                    if var_obj.isArray():
                        Logger.get_instance().log_error(f"Cannot use array in binary operation")
        # Check that all variables used are defined
        self.check_is_defined(leaves, "binary expression")

        self.visitChildren(node)

    def visitBranch(self, node: BranchNode):
        parentNode = node.parent

        # return outside a function
        if node.sort == "return":
            found = False
            if not look_in_parent(node, FunctionNode, found):
                Logger.get_instance().log_error("Cannot return outside of a function.")

            if node.children:
                to_return = node.children[0]
                self.check_is_defined([to_return], "return statement")
        else:
            found = False
            if not look_in_parent(node, LoopNode, found):
                Logger.get_instance().log_error("Invalid use of loop control statement.")

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
        function_obj = self.symbol_table.get_variable(node.name)
        leaves = []
        extract_leaves(node, leaves)
        if not function_obj.name == "scanf":
            self.check_is_defined(leaves, "function call")

        if function_obj.args and len(node.children) != len(function_obj.args):
            Logger.get_instance().log_error(f"Function {function_obj.name} expected {len(function_obj.args)} arguments,"
                             f" got {len(node.children)} instead.")
        if not function_obj.args:
            # printf or scanf
            if len(node.children) > 1:
                arguments_node: LiteralNode = node.children[0]
                arguments_string = arguments_node.value

                func_types = extract_print_types(arguments_string) if node.name == "printf" else extract_scan_types(arguments_string)

                # Make sure same amount of arguments
                if len(func_types) != len(node.children[1:]):
                    Logger.get_instance().log_error(f"printf function expected {len(func_types)} arguments, "
                                     f"got {len(node.children[1:])}")

                # Make sure type of argument matches
                for func_type, arg_node in zip(func_types, node.children[1:]):
                    if isinstance(arg_node, LiteralNode):
                        arg_type = arg_node.type.name
                    elif isinstance(arg_node, VariableNode):
                        var_name = arg_node.name
                        var_obj = self.symbol_table.get_variable(var_name)

                        # mark as defined after scanf
                        if function_obj.name == "scanf":
                            self.symbol_table.alter_identifier(var_name, is_assigned=True)

                        arg_type = var_obj.type_.name
                        if var_obj.isArray():
                            arg_type += "[]"
                    else:
                        # mark leaves as defined
                        leaves = []
                        extract_leaves(arg_node, leaves)
                        for leaf in leaves:
                            if isinstance(leaf, VariableNode):
                                var_name = leaf.name
                                self.symbol_table.alter_identifier(var_name, is_assigned=True)

                        continue
                    if "s" in func_type and arg_type not in ["STRING", "CHAR[]"]:
                        Logger.get_instance().log_error(f"{function_obj.name} expected {func_type}, but did not get a string")

                    if arg_type in ["STRING", "CHAR[]"] and "s" not in func_type:
                        Logger.get_instance().log_error(f"{function_obj.name} expected {func_type}, but got a string instead")

        self.visitChildren(node)

    def visitFunction(self, node: FunctionNode):
        type_node = node.children[0]
        variable_node = node.children[1]
        is_defined = isinstance(node.children[-1], ScopeNode)

        args_nodes = [child for child in node.children if isinstance(child, FunctionArgumentNode)]
        args_count = len(args_nodes)

        if variable_node.name == "main" and type_node.type.type.name == "INT" and args_count == 0:
            self.found_main = True

        returns = False
        if returns_something(node, returns) and type_node.type.type == TypeEnum.VOID:
            Logger.get_instance().log_error("Returning something in void function.")

        if not returns_something(node, returns) and type_node.type.type != TypeEnum.VOID:
            Logger.get_instance().log_warning(f"Non-void function {variable_node.name} does not always end in a return statement")

        # parameter redefinition
        args_names = [child.name for child in node.children if isinstance(child, FunctionArgumentNode)]
        if has_duplicates(args_names):
            Logger.get_instance().log_error("Cannot redefine function parameters.")

        # definition of predeclared function
        forward_declaration: Function = self.symbol_table.get_variable(variable_node.name, expected=False)
        if forward_declaration:
            # make sure it is not redefined
            if forward_declaration.is_assigned:
                Logger.get_instance().log_error(f"Redefinition of function {variable_node.name}")

            # make sure it has the same return value
            if forward_declaration.type_ != type_node.type.type:
                Logger.get_instance().log_error(f"Definition of forward declared function {variable_node.name} "
                                 f"has a different return type.")

            # make sure it has the same number of arguments
            if len(forward_declaration.args) != args_count:
                Logger.get_instance().log_error(f"Definition of forward declared function {variable_node.name} "
                                 f"expected {len(forward_declaration.args)} arguments, got {args_count} instead.")

            # make sure the type of the arguments is the same
            for index, (previous_variable, current_node) in enumerate(zip(forward_declaration.args, args_nodes)):
                if previous_variable.type_ != current_node.type.type:
                    Logger.get_instance().log_error(f"Definition of forward declared function {variable_node.name} "
                                    f"expected argument {index+1} to be type {previous_variable.type_.name}, "
                                     f"got {current_node.type.type.name} instead.")

            self.symbol_table.alter_identifier(
                name=variable_node.name,
                is_assigned=True
            )
        else:
            args_objs = []
            for arg_node in args_nodes:
                args_objs.append(
                    Variable(
                        name=arg_node.name,
                        type_=arg_node.type.type,
                        is_const=arg_node.type.is_const,
                        is_defined=True,
                        ptr_level=arg_node.type.pointer_level
                    )
                )
            function_obj = Function(
                name=variable_node.name,
                type_=type_node.type.type,
                is_const=type_node.type.is_const,
                is_defined=is_defined,
                ptr_level=type_node.type.pointer_level,
                args=args_objs
            )
            self.symbol_table.add_variable(function_obj)

        self.visitChildren(node)

    def visitInclude(self, node: IncludeNode):
        if node.to_include != "stdio.h":
            Logger.get_instance().log_error(f"Invalid include of file {node.to_include}")
        printf_func = Function(
            name="printf",
            type_=TypeEnum.INT,
            is_const=False,
            is_defined=True,
            ptr_level=0,
            args=None
        )
        scanf_func = Function(
            name="scanf",
            type_=TypeEnum.INT,
            is_const=False,
            is_defined=True,
            ptr_level=0,
            args=None
        )
        self.symbol_table.add_variable(printf_func)
        self.symbol_table.add_variable(scanf_func)
        self.visitChildren(node)

    def visitLiteral(self, node: LiteralNode):

        if isinstance(node.parent, UnaryExpressionNode):
            parentNode = node.parent
            if parentNode.operator == "*":
                Logger.get_instance().log_error(f"Cannot dereference a literal of type {node.type.name}")

        self.visitChildren(node)

    def visitLoop(self, node: LoopNode):
        self.visitChildren(node)

    def visitScope(self, node: ScopeNode):
        self.symbol_table.add_scope(scope=Scope())

        # Add arguments
        parent_node = node.parent
        if isinstance(parent_node, FunctionNode):
            argument_nodes = parent_node.children[2:-1]
            for arg_node in argument_nodes:
                variable_obj = Variable(
                    name=arg_node.name,
                    type_=arg_node.type.type,
                    is_const=arg_node.type.is_const,
                    is_defined=True,
                    ptr_level=arg_node.type.pointer_level
                )

                self.symbol_table.add_variable(variable_obj)

        self.visitChildren(node)

        if not node.parent and not self.found_main:
            Logger.get_instance().log_error("Main not defined")

        self.symbol_table.leave_scope()

    def visitType_declaration(self, node: TypeDeclarationNode):
        self.visitChildren(node)

    def visitUnary_expression(self, node: UnaryExpressionNode):
        if node.operator in ["++", "--"]:
            child = node.children[0]
            if isinstance(child, VariableNode):
                self.check_not_const(child)
        operand_node = node.children[0]
        self.check_is_defined([operand_node], "unary expression")
        if node.operator in ["&", "++", "--"]:
            if not isinstance(operand_node, VariableNode) and \
                    not (isinstance(operand_node, UnaryExpressionNode) and operand_node.operator == "*")\
                    and not (isinstance(operand_node, BinaryExpressionNode) and operand_node.operator == "[]"):
                Logger.get_instance().log_error("Dereference expected lvalue")

        self.visitChildren(node)

    def visitVariable_definition(self, node: VariableDefinitionNode):
        is_defined = len(node.children) > 0
        if node.is_array:
            # Check that the array size is an integer
            if node.has_array_size:
                array_size_node: LiteralNode = node.children[0]
                if array_size_node.type != TypeEnum.INT:
                    Logger.get_instance().log_error("Array index should be of type int")
            variable_obj = Array(
                name=node.name,
                type_=node.type.type,
                is_const=node.type.is_const,
                is_defined=is_defined,
                ptr_level=node.type.pointer_level,
                array_size=-1  # TODO
            )
        else:
            variable_obj = Variable(
                name=node.name,
                type_=node.type.type,
                is_const=node.type.is_const,
                is_defined=is_defined,
                ptr_level=node.type.pointer_level
            )
            if is_defined:
                leaves = []
                extract_leaves(node, leaves)
                self.check_is_defined(leaves, "variable definition")

                left_type = node.type.type.value
                right_type = get_type(node, self.symbol_table)
                # right_type = -1
                # for leaf in leaves:
                #     if isinstance(leaf, LiteralNode):
                #         if leaf.type.value > right_type:
                #             right_type = leaf.type.value
                #     elif isinstance(leaf, VariableNode):
                #         var_name = leaf.name
                #         var_obj = self.symbol_table.get_variable(var_name)
                #         if var_obj.type_.value > right_type:
                #             right_type = var_obj.type_.value

                if left_type < right_type.value:
                    Logger.get_instance().log_warning(f"Implicit conversion from "
                                                      f"{TypeEnum(right_type).name} to {TypeEnum(left_type).name}")

        self.symbol_table.add_variable(variable_obj)

        self.visitChildren(node)

    def visitVariable(self, node: VariableNode):
        self.symbol_table.get_variable(node.name)
        self.visitChildren(node)
