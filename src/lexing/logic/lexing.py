import ast
import tokenize
from io import BytesIO

class JayLinter(ast.NodeVisitor):
    def __init__(self, source_code):
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.tokens = list(tokenize.tokenize(BytesIO(source_code.encode('utf-8')).readline))
        self.messages = []

    def _has_preceding_comment(self, func_lineno):
        for token in self.tokens:
            if token.start[0] == func_lineno - 1 and token.type == tokenize.COMMENT:
                return True
        return False

    def visit_FunctionDef(self, node):
        if not self._has_preceding_comment(node.lineno):
            self.messages.append(f"Function '{node.name}' lacks a preceding comment.")
        self.generic_visit(node)

    def lint(self):
        tree = ast.parse(self.source_code)
        self.visit(tree)
        return self.messages

