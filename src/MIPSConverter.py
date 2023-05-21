from src.MIPSInterface import MIPSInterface
from src.SymbolTable import SymbolTable
from src.visitors.MIPSConversionDataVisitor import MIPSConversionDataVisitor
from src.visitors.MIPSConversionTextVisitor import MIPSConversionTextVisitor


class MIPSConverter:
    def __init__(self, symbol_table: SymbolTable):
        self.mips_interface = MIPSInterface()
        self.mips_conversion_data_visitor = MIPSConversionDataVisitor(
            mips_interface=self.mips_interface,
            symbol_table=symbol_table
        )
        self.mips_conversion_text_visitor = MIPSConversionTextVisitor(
            mips_interface=self.mips_interface,
            symbol_table=symbol_table
        )

    def convert(self, root):
        self.mips_conversion_data_visitor.visitScope(root)
        self.mips_conversion_text_visitor.visitScope(root)
        self.mips_interface.write_to_file("tests/output/mips/test.asm")
