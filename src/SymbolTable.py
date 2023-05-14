class Variable:
    def __init__(self, name="", type_="", is_const=False, is_defined=False, ptr_level=0):
        self.name = name
        self.type_ = type_
        self.is_const = is_const
        self.is_assigned = is_defined
        self.ptr_level = ptr_level

    def isArray(self):
        return False

    def isFunction(self):
        return False


class Array(Variable):
    def __init__(self, name="", type_="", is_const=False, is_defined=False, ptr_level=0, array_size=0):
        super().__init__(name, type_, is_const, is_defined, ptr_level)
        self.array_count = array_size

    def isArray(self):
        return True


class Function(Variable):
    def __init__(self, name="", type_="", is_const=False, is_defined=False, ptr_level=0, args: list[Variable] = None):
        super().__init__(name, type_, is_const, is_defined, ptr_level)
        self.args_count = args_count

    def isFunction(self):
        return True


class Scope:
    def __init__(self, name="", parent_scope=None):
        self.name = name
        self.parent_scope = parent_scope
        self.table = {}

    def add_variable(self, variable):
        # search in current scope
        if variable.name in self.table.keys():
            if self.table[variable.name].is_assigned:
                raise ValueError(f"Variable {variable.name} already defined in this scope.")
            else:
                raise ValueError(f"Variable {variable.name} already declared in this scope.")

        self.table[variable.name] = variable

    def get_variable(self, identifier: str, expected: bool = True):
        # search in current scope
        for variable in reversed(self.table.values()):
            if identifier == variable.name:
                return self.table[identifier]
        # search in parent scope too
        if self.parent_scope and self.parent_scope.get_variable(identifier, expected):
            return self.parent_scope.get_variable(identifier, expected)

        if expected:
            raise ValueError(f"Variable {identifier} not defined.")
        else:
            return None

    def check_is_assigned(self, identifier: str):
        return self.get_variable(identifier).is_assigned

    def check_is_const(self, identifier: str):
        return self.get_variable(identifier).is_const

    def alter_identifier(self, name, type_=None, is_const=None, is_assigned=None, ptr_level=None, array_size=None, args_count=None):
        previous_variable = self.get_variable(name)

        new_type = type_ if type_ else previous_variable.type_
        new_is_const = is_const if is_const else previous_variable.is_const
        new_is_assigned = is_assigned if is_assigned else previous_variable.is_assigned
        new_ptr_level = ptr_level if ptr_level else previous_variable.ptr_level
        
        if previous_variable.isArray():
            new_array_size = array_size if array_size else previous_variable.array_size
            self.table[name] = \
                Array(name, new_type, new_is_const, new_is_assigned, new_ptr_level, new_array_size)
        elif previous_variable.isFunction():
            new_args_count = args_count if args_count else previous_variable.args_count
            self.table[name] = \
                Function(name, new_type, new_is_const, new_is_assigned, new_ptr_level)
        else:
            self.table[name] = \
                Variable(name, new_type, new_is_const, new_is_assigned, new_ptr_level)


class SymbolTable:
    def __init__(self):
        self.current_scope: Scope = Scope("global")
        self.scopes: list[Scope] = [self.current_scope]

    def add_scope(self, scope: Scope):
        scope.parent_scope = self.current_scope
        self.scopes.append(scope)
        self.enter_scope(scope)

    def enter_scope(self, scope: Scope):
        assert (scope in self.scopes)
        self.current_scope = scope

    def leave_scope(self):
        self.enter_scope(self.current_scope.parent_scope)

    def add_variable(self, variable):
        assert (self.current_scope is not None)
        self.current_scope.add_variable(variable)

    def get_variable(self, identifier: str, expected: bool = True):
        assert (self.current_scope is not None)
        return self.current_scope.get_variable(identifier=identifier, expected=expected)

    def get_scope(self, name: str):
        for scope in self.scopes:
            if not scope:
                continue
            if scope.name == name:
                return scope
        raise ValueError(f"Could not find scope with name {name}.")

    def check_is_const(self, identifier: str):
        assert (self.current_scope is not None)
        return self.current_scope.check_is_const(identifier)

    def check_is_assigned(self, identifier: str):
        assert (self.current_scope is not None)
        return self.current_scope.check_is_assigned(identifier)

    def alter_identifier(self, name, type_=None, is_const=None, is_assigned=None, ptr_level=None, array_size=None, args_count=None):
        self.current_scope.alter_identifier(name, type_, is_const, is_assigned, ptr_level, array_size, args_count)
