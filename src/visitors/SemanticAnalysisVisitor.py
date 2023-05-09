from src.SymbolTable import *
from src.visitors.ASTVisitor import ASTVisitor
from src.ast_nodes import *
from src.Util import auto_cast, TypeEnum, returns_something


class SemanticAnalysisVisitor(ASTVisitor):
    def __init__(self):
        super().__init__()
        self.symbol_table: SymbolTable = SymbolTable()

    def visitArray_assignment(self, node: ArrayAssignmentNode):
        if not isinstance(node.index, int):
            raise ValueError("The index of an array must be an integer.")
        self.visitChildren(node)

    def visitAssignment(self, node: AssignmentNode):
        assignee = node.children[0]
        if isinstance(assignee, FunctionCallNode):
            function_obj = self.symbol_table.get_variable(assignee.name)
            assigned_obj = self.symbol_table.get_variable(node.name)
            if function_obj.type_ == TypeEnum.VOID:
                raise ValueError(
                    f"Incompatible assignment from type {function_obj.type_.name} to {assigned_obj.type_.name}")

        self.visitChildren(node)

    def visitBinary_expression(self, node: BinaryExpressionNode):
        if node.operator == "[]":
            index_node: LiteralNode = node.children[1]
            if not isinstance(auto_cast(index_node.value), int):
                raise ValueError("The index of an array must be an integer.")
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
        function_obj = self.symbol_table.get_variable(node.name)
        if len(node.children) != function_obj.args_count:
            raise ValueError(f"Function {function_obj.name} expected {function_obj.args_count} arguments,"
                             f" got {len(node.children)} instead.")
        self.visitChildren(node)

    def visitFunction(self, node: FunctionNode):
        type_node = node.children[0]
        variable_node = node.children[1]
        is_defined = isinstance(node.children[-1], ScopeNode)

        args_count = len([child for child in node.children if isinstance(child, FunctionArgumentNode)])

        returns = False
        if returns_something(node, returns) and type_node.type.type == TypeEnum.VOID:
            raise ValueError("Returning something in void function.")

        function_obj = Function(
            name=variable_node.name,
            type_=type_node.type.type,
            is_const=type_node.type.is_const,
            is_defined=is_defined,
            ptr_level=0,  # TODO: Determine this
            args_count=args_count
        )
        self.symbol_table.add_variable(function_obj)
        self.visitChildren(node)

    def visitInclude(self, node: IncludeNode):
        if node.to_include != "stdio.h":
            raise ValueError(f"Invalid include of file {node.to_include}")
        self.visitChildren(node)

    def visitLiteral(self, node: LiteralNode):
        self.visitChildren(node)

    def visitLoop(self, node: LoopNode):
        self.visitChildren(node)

    def visitScope(self, node: ScopeNode):
        self.symbol_table.add_scope(scope=Scope())
        self.visitChildren(node)
        self.symbol_table.leave_scope()

    def visitType_declaration(self, node: TypeDeclarationNode):
        self.visitChildren(node)

    def visitUnary_expression(self, node: UnaryExpressionNode):
        operand_node = node.children[0]
        if node.operator == "&":
            if not isinstance(operand_node, VariableNode) and \
                    not (isinstance(operand_node, UnaryExpressionNode) and operand_node.operator == "*"):
                raise ValueError("Dereference expected lvalue")
        self.visitChildren(node)

    def visitVariable_definition(self, node: VariableDefinitionNode):
        is_defined = len(node.children) == 0
        variable_obj = Variable(
            name=node.name,
            type_=node.type.type,
            is_const=node.type.is_const,
            is_defined=is_defined,
            ptr_level=0  # TODO
        )
        self.symbol_table.add_variable(variable_obj)
        self.visitChildren(node)

    def visitVariable(self, node: VariableNode):
        self.visitChildren(node)
