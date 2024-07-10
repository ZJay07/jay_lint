import ast
import tokenize
from io import BytesIO

class JayLinter(ast.NodeVisitor):
    def __init__(self, source_code):
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.tokens = list(tokenize.tokenize(BytesIO(source_code.encode('utf-8')).readline))
        self.messages = []
        self.import_lines = []

    def _has_preceding_comment(self, func_lineno):
        for token in self.tokens:
            if token.start[0] == func_lineno - 1 and token.type == tokenize.COMMENT:
                return True
        return False

    def visit_FunctionDef(self, node):
        if not self._has_preceding_comment(node.lineno):
            self.messages.append(f"Function '{node.name}' lacks a preceding comment.")
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.import_lines.append((alias.name, node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            full_name = f"{node.module}.{alias.name}" if node.module else alias.name
            self.import_lines.append((full_name, node.lineno))
        self.generic_visit(node)

    def check_import_order(self):
        sorted_imports = sorted(self.import_lines, key=lambda x: x[0])
        if self.import_lines != sorted_imports:
            self.messages.append("Imports are not in lexicographical order.")

    def lint(self):
        tree = ast.parse(self.source_code)
        self.visit(tree)
        self.check_import_order()
        return self.messages

