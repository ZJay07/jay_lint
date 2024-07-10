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
        self.imported_names = set()
        self.used_names = set()
        self.function_args = {}

    def _has_preceding_comment(self, func_lineno):
        for token in self.tokens:
            if token.start[0] == func_lineno - 1 and token.type == tokenize.COMMENT:
                return True
        return False

    def visit_FunctionDef(self, node):
        if not self._has_preceding_comment(node.lineno):
            self.messages.append(f"Function '{node.name}' lacks a preceding comment.")
        
        arg_names = {arg.arg for arg in node.args.args}
        self.function_args[node.name] = arg_names
        
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.import_lines.append((alias.name, node.lineno))
            self.imported_names.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            full_name = f"{node.module}.{alias.name}" if node.module else alias.name
            self.import_lines.append((full_name, node.lineno))
            self.imported_names.add(full_name)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def check_import_order(self):
        sorted_imports = sorted(self.import_lines, key=lambda x: x[0])
        if self.import_lines != sorted_imports:
            self.messages.append("Imports are not in lexicographical order.")

    def check_trailing_whitespace(self):
        for i, line in enumerate(self.source_lines, start=1):
            if line.rstrip() != line:
                self.messages.append(f"Line {i} has trailing whitespace.")
            if line == '':
                self.messages.append(f"Line {i} is empty.")

    def check_unused_imports(self):
        unused_imports = self.imported_names - self.used_names
        for name in unused_imports:
            lineno = next(line for (imp, line) in self.import_lines if imp == name)
            self.messages.append(f"Import '{name}' on line {lineno} is not used.")

    def check_unused_function_args(self):
        for func_name, args in self.function_args.items():
            unused_args = args - self.used_names
            for arg in unused_args:
                self.messages.append(f"Function '{func_name}' has an unused argument '{arg}'.")

    def check_unused_variables(self):
        assigned_names = {node.id for node in ast.walk(ast.parse(self.source_code)) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)}
        unused_vars = assigned_names - self.used_names
        for var in unused_vars:
            lineno = next(node.lineno for node in ast.walk(ast.parse(self.source_code)) if isinstance(node, ast.Name) and node.id == var)
            self.messages.append(f"Variable '{var}' assigned on line {lineno} is not used.")

    def check_empty_lines(self):
        previous_line_empty = False
        previous_line_was_import = False
        previous_line_was_function = False

        for i, line in enumerate(self.source_lines, start=1):
            stripped_line = line.strip()
            if stripped_line == '':
                previous_line_empty = True
                continue

            if previous_line_empty:
                previous_line_empty = False
                if previous_line_was_import and not stripped_line.startswith(('import ', 'from ')):
                    previous_line_was_import = False
                    continue

                if previous_line_was_function and not stripped_line.startswith('def '):
                    previous_line_was_function = False
                    continue

                self.messages.append(f"Line {i} should be empty.")
            else:
                if stripped_line.startswith(('import ', 'from ')):
                    previous_line_was_import = True
                elif stripped_line.startswith('def '):
                    previous_line_was_function = True
                elif not previous_line_was_function and not previous_line_was_import:
                    self.messages.append(f"Line {i} should be empty.")
    
        # Check if the last line is not empty
        if self.source_lines and self.source_lines[-1].strip() != '':
            self.messages.append("File should end with an empty line.")


    def lint(self):
        tree = ast.parse(self.source_code)
        self.visit(tree)
        self.check_import_order()
        self.check_trailing_whitespace()
        self.check_unused_imports()
        self.check_unused_function_args()
        self.check_unused_variables()
        self.check_empty_lines()
        return self.messages
