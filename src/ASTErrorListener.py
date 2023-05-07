from antlr4 import error


class ASTErrorListener(error.ErrorListener.ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise ValueError(f"[Syntax Error] line {line}, position {column}: {msg}")
