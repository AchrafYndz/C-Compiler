import sys
from antlr4 import error

from src.Logger import Logger


class ASTErrorListener(error.ErrorListener.ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        Logger.get_instance().log_syntax_error(f"line {line}, position {column}: {msg}")
