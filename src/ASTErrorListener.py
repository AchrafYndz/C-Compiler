import sys
from antlr4 import error
import logging

logging.basicConfig(format="%(message)s")

class ASTErrorListener(error.ErrorListener.ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        logging.error(f"[Syntax Error] line {line}, position {column}: {msg}")
        sys.exit()
