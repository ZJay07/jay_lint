import ast
import logging

green_start = "\033[92m"
# For printing in red
red_start = "\033[91m"
# Reset color
color_reset = "\033[0m"

class FunctionArgLinter(ast.NodeVisitor):
    def __init__(self, max_args, source_lines, max_line_length=79):
        self.max_args = max_args
        self.source_lines = source_lines
        self.max_line_length = max_line_length
        self.messages = []
        self.used_names = set()
        self.imported_names = []
        self.import_lines = []

        # Set up logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def visit_FunctionDef(self, node):
        if not self._has_preceding_comment(node):
            self.messages.append(f"{red_start}Function '{node.name}' lacks a preceding comment.")
        
        num_args = len(node.args.args)
        if num_args > self.max_args:
            self.messages.append(f"{red_start}Function '{node.name}' has too many arguments ({num_args}).")

        self.check_unused_args(node)
        self.generic_visit(node)

    def _has_preceding_comment(self, node):
        func_lineno = node.lineno
        comment_lineno = func_lineno - 1
        if comment_lineno > 0 and self.source_lines[comment_lineno - 1].strip().startswith("#"):
            return True
        return False

    def check_line_length(self):
        for i, line in enumerate(self.source_lines, start=1):
            if len(line) > self.max_line_length:
                self.messages.append(f"{red_start}Line {i} exceeds {self.max_line_length} characters.")

    def check_unused_args(self, node):
        arg_names = {arg.arg for arg in node.args.args}
        self.used_names = set()

        for sub_node in ast.walk(node):
            if isinstance(sub_node, ast.Name) and isinstance(sub_node.ctx, ast.Load):
                self.used_names.add(sub_node.id)

        unused_args = arg_names - self.used_names
        for arg in unused_args:
            self.messages.append(f"{red_start}Function '{node.name}' has an unused argument '{arg}'.")

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names.append(name)
            self.import_lines.append((name, node.lineno))
            self.logger.debug(f"Import added: {name} on line {node.lineno}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names.append(name)
            self.import_lines.append((name, node.lineno))
            self.logger.debug(f"ImportFrom added: {name} on line {node.lineno}")
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
            self.logger.debug(f"Name used: {node.id}")
        self.generic_visit(node)

    def check_unused_imports(self):
        self.logger.debug(f"Checking unused imports. Imported names: {self.imported_names}, Used names: {self.used_names}")
        unused_imports = set(self.imported_names) - set(self.used_names)
        for name in unused_imports:
            lineno = dict(self.import_lines)[name]
            self.messages.append(f"{red_start}Import '{name}' on line {lineno} is not used.")

    def check_import_order(self):
        sorted_imports = sorted(self.import_lines, key=lambda x: x[0])
        if self.import_lines != sorted_imports:
            self.messages.append("{red_start}Imports are not in lexicographical order.")

    def visit(self, node):
        super().visit(node)

    def finalize(self):
        self.check_unused_imports()
        self.check_import_order()

