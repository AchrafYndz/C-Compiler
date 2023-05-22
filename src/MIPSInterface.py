from src.Type import TypeEnum, Type
from src.Util import float_to_hex


class MIPSInterface:
    def __init__(self):
        self.data = {}
        self.text = []
        self.move("fp", "sp")
        self.jump_and_link("main")
        self.exit()

        self.global_variables = {}
        self.local_variables = {}  # var_name: int
        self.current_offset = 0
        self.local_offset = 0

    def exit(self):
        self.load_immediate("v0", 10)
        self.syscall()

    def syscall(self):
        self.append_instruction("syscall")

    def load_immediate(self, register, value):
        self.append_instruction(f"li ${register}, {value}")

    def subtract_unsigned(self, register1, register2, value):
        self.append_instruction(f"subu ${register1}, ${register2}, {value}")

    def add_immediate_unsigned(self, register1, register2, value):
        self.append_instruction(f"addiu ${register1}, ${register2}, {value}")

    def add_unsigned(self, register1, register2, register3):
        self.append_instruction(f"addu ${register1}, ${register2}, ${register3}")

    def append_string(self, string: str):
        string = string.replace('"', '')
        label = string.replace(' ', '_') + "_" + str(len(self.data))
        self.data[string] = label

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

    def append_variable(self, var_name):
        self.store_word("t0", self.local_offset, "sp")
        self.local_variables[var_name] = self.local_offset
        self.local_offset += 4

    def store_in_variable(self, var_name):
        offset = self.local_variables[var_name]
        self.store_word("t0", offset, "sp")

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
        for string, label in self.data.items():
            file.write(label + ": .asciiz \"" + string + '\" \n')
        file.write('\n')

        file.write(".text\n")
        for line in self.text:
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

