from src.Type import TypeEnum, Type
from src.Util import float_to_hex


class MIPSInterface:
    def __init__(self):
        self.variable = {}
        self.data = []
        self.text = []
        self.move("fp", "sp")
        self.jump_and_link("main")
        self.exit()

        self.global_variables = {}
        self.local_variables = {}  # var_name: int
        self.current_offset = 0
        self.local_offset = 0

        self.free_registers = [f"t{i}" for i in range(8)]
        self.last_expression_registers = []

    def get_free_register(self):
        return self.free_registers.pop(0)

    def free_up_registers(self, registers):
        if any([register in self.free_registers for register in registers]):
            raise ValueError("Trying to free a register that should already be free")
        self.free_registers += registers

    def _swap_immediate_values(self, immediate_value, argument):
        # load the immediate value into a register
        self.load_immediate("t0", immediate_value)
        return "t0", argument

    def exit(self):
        self.load_immediate("v0", 10)
        self.syscall()

    def syscall(self):
        self.append_instruction("syscall")

    def load_immediate(self, register, value):
        self.append_instruction(f"li ${register}, {value}")

    def add_immediate_unsigned(self, register, argument1, argument2):
        self.append_instruction(f"addiu ${register}, ${argument1}, {argument2}")

    def subtract_immediate_unsigned(self, register, argument1, argument2):
        self.append_instruction(f"subiu ${register}, ${argument1}, {argument2}")

    def subtract_unsigned(self, register, argument1, argument2, is_float=False):
        operation = "subu" if not is_float else "sub.s"
        self.append_instruction(f"{operation} ${register}, ${argument1}, ${argument2}")

    def add_unsigned(self, register, argument1, argument2, is_float=False):
        operation = "addu" if not is_float else "add.s"
        self.append_instruction(f"{operation} ${register}, ${argument1}, ${argument2}")

    def multiply(self, register, argument1, argument2, is_float=False):
        operation = "mul" if not is_float else "mul.s"
        self.append_instruction(f"{operation} ${register}, ${argument1}, ${argument2}")

    def divide(self, register, argument1, argument2, is_float=False):
        operation = "div" if not is_float else "div.s"
        self.append_instruction(f"{operation} ${register}, ${argument1}, ${argument2}")

    def modulo(self, register, argument1, argument2, is_float=False):
        assert (not is_float)
        self.append_instruction(f"rem ${register}, ${argument1}, ${argument2}")

    def strictly_less(self, register, argument1, argument2, is_float=False):
        self.append_instruction(f"slt ${register}, ${argument1}, ${argument2}")

    def strictly_greater(self, register, argument1, argument2, is_float=False):
        self.append_instruction(f"sgt ${register}, ${argument1}, ${argument2}")

    def less_or_equal(self, register, argument1, argument2, is_float=False):
        self.append_instruction(f"sle ${register}, ${argument1}, ${argument2}")

    def greater_or_equal(self, register, argument1, argument2, is_float=False):
        self.append_instruction(f"sge ${register}, ${argument1}, ${argument2}")

    def equal(self, register, argument1, argument2, is_float=False):
        self.append_instruction(f"seq ${register}, ${argument1}, ${argument2}")

    def not_equal(self, register, argument1, argument2, is_float=False):
        self.append_instruction(f"sne ${register}, ${argument1}, ${argument2}")

    def branch_equal(self, register, argument1, argument2, is_float=False):
        self.append_instruction(f"beq ${register}, {argument1}, {argument2}")
    def logical_and(self, register, argument1, argument2, is_float=False):
        self.append_instruction(f"and ${register}, ${argument1}, ${argument2}")

    def logical_or(self, register, argument1, argument2, is_float=False):
        self.append_instruction(f"or ${register}, ${argument1}, ${argument2}")

    def logical_not(self, register, argument):
        self.append_instruction(f"sltu ${register}, $zero, ${argument}")
        self.append_instruction(f"xori ${register}, ${register}, 1")

    def append_string(self, string: str):
        string = string.replace('"', '')
        label = string.replace(' ', '_') + "_" + str(len(self.variable))
        self.variable[string] = label

    def append_array(self, array_name: str, size: int):
        instruction = f"{array_name}: .space {size * 4}"
        self.data.append(instruction)

    def append_instruction(self, instr: str):
        self.text.append(instr)

    def append_label(self, label_name: str):
        self.append_instruction(label_name + ":")

    def append_global_variable(self, variable_name, value, type_: Type):
        self.global_variables[variable_name] = self.current_offset
        if type_.type == TypeEnum.FLOAT:
            value = float_to_hex(float(value))
        self.load_immediate("s0", value)
        if type_.type == TypeEnum.FLOAT:
            self.move_to_c1("s0", "f0")
            self.store_word_c1("f0", self.current_offset, "gp")
        else:
            self.store_word("s0", self.current_offset, "gp")
        self.current_offset -= 4

    def append_variable(self, register, var_name):
        self.store_word(register, self.local_offset, "sp")
        self.local_variables[var_name] = self.local_offset
        self.local_offset += 4

    def store_in_variable(self, var_name, register="t0"):
        offset = self.local_variables[var_name]
        self.store_word(register, offset, "sp")

    def load_variable(self, register, var_name):
        offset = self.local_variables[var_name]
        self.load_word(register, offset, "sp")

    def store_word(self, register1, offset, register2):
        self.append_instruction(f"sw ${register1}, {offset}(${register2})")

    def load_word(self, register1, offset, register2):
        self.append_instruction(f"lw ${register1}, {offset}(${register2})")

    def load_address(self, register1, label):
        self.append_instruction(f"la ${register1}, {label}")

    def jump(self, label_name: str):
        self.append_instruction(f"j {label_name}")

    def jump_and_link(self, label_name: str):
        self.append_instruction(f"jal {label_name}")

    def jump_register(self, register_name: str):
        self.append_instruction(f"jr ${register_name}")

    def move(self, reg1, reg2):
        self.append_instruction(f"move ${reg1}, ${reg2}")

    def enter_function(self, function_name: str):
        self.append_label(function_name)

    def leave_function(self):
        self.jump_register("ra")
        self.append_instruction("nop")

    def write_to_file(self, filename):
        file = open(filename, "w")
        file.write(".data\n")
        for string, label in self.variable.items():
            file.write(label + ": .asciiz \"" + string + '\" \n')
        for line in self.data:
            file.write(line + '\n')
        file.write('\n')

        file.write(".text\n")
        for line in self.text:
            if line[-1] == ":":
                file.write("\n")
            file.write(line + '\n')
        file.close()

    def move_to_c1(self, register1, register2):
        self.append_instruction(f"mtc1 ${register1}, ${register2}")

    def store_word_c1(self, register1, offset, register2):
        self.append_instruction(f"swc1 ${register1}, {offset}(${register2})")

    def print(self, value, type_: TypeEnum=None, is_variable=False):
        v0_arguments = {
            TypeEnum.INT: 1,
            TypeEnum.FLOAT: 2,
            TypeEnum.STRING: 4,
            TypeEnum.CHAR: 11
        }
        v0_argument = v0_arguments[type_]
        if is_variable:
            self.move("a0", "t0")
        elif v0_argument == 4:
            self.load_address("a0", value)
        else:
            self.load_immediate("a0", value)
        self.load_immediate("v0", v0_argument)  # TODO: for now only ints
        self.syscall()

    def scan(self, var_name):
        self.load_immediate("v0", 5)
        self.syscall()
        self.store_in_variable(var_name, "v0")
