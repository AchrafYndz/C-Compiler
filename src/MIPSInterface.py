class MIPSInterface:
    def __init__(self):
        self.data = []
        self.text = []

    def append_string(self, string: str):
        string = string.replace('"', '')
        label = string.replace(' ', '_') + "_" + str(len(self.data))
        self.data.append(f"{label}: .asciiz \"{string}\"")

    def append_instruction(self, instr: str):
        self.text.append(instr)

    def append_label(self, label_name: str):
        self.append_instruction(label_name + ":")

    def append_global_variable(self, variable_name, value):
        self.append_label(variable_name)
        self.append_instruction(f".4byte {value}")

    def jump_register(self, register_name: str):
        self.append_instruction(f"jr ${register_name}")

    def enter_function(self, function_name: str):
        self.append_label(function_name)

    def leave_function(self):
        self.jump_register("ra")
        self.append_instruction("nop")

    def write_to_file(self, filename):
        file = open(filename, "w")
        file.write(".data\n")
        for line in self.data:
            file.write(line + '\n')
        file.write('\n')

        file.write(".text\n")
        for line in self.text:
            file.write(line + '\n')
        file.close()
