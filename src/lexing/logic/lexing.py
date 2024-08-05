import ast
import tokenize
from io import BytesIO
import re
import sys

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
        self.unused_imports = set()
        self.unused_variables = set()
        self.class_attributes = {}
        self.used_class_attributes = set()
        self.current_class = None

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

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.class_attributes[self.current_class] = set()
        self.generic_visit(node)
        self.current_class = None

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
    
    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_class_attributes.add(node.attr)
        elif isinstance(node.ctx, ast.Store) and isinstance(node.value, ast.Name) and node.value.id == 'self':
            if self.current_class:
                self.class_attributes[self.current_class].add(node.attr)
        self.generic_visit(node)

    def visit_Return(self, node):
        # Check for blank lines before return statements
        return_lineno = node.lineno
        if return_lineno > 1 and self.source_lines[return_lineno - 2].strip() == "":
            self.messages.append(f"Line {return_lineno} has a blank line before 'return' statement.")
        self.generic_visit(node)

    def check_import_order(self):
        sorted_imports = sorted(self.import_lines, key=lambda x: x[0])
        if self.import_lines != sorted_imports:
            self.messages.append("Imports are not in lexicographical order.")

    def check_trailing_whitespace(self):
        for i, line in enumerate(self.source_lines, start=1):
            if line.rstrip() != line:
                self.messages.append(f"Line {i} has trailing whitespace.")
            if line == '' and i != 1:
                self.messages.append(f"Line {i} is empty.")

    def check_unused_imports(self):
        self.unused_imports = self.imported_names - self.used_names
        for name in self.unused_imports:
            lineno = next(line for (imp, line) in self.import_lines if imp == name)
            self.messages.append(f"Import '{name}' on line {lineno} is not used.")

    def check_unused_function_args(self):
        for func_name, args in self.function_args.items():
            unused_args = args - self.used_names
            for arg in unused_args:
                self.messages.append(f"Function '{func_name}' has an unused argument '{arg}'.")

    def check_unused_variables(self):
        assigned_names = {node.id for node in ast.walk(ast.parse(self.source_code)) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)}
        self.unused_variables = assigned_names - self.used_names
        for var in self.unused_variables:
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
                    if previous_line_was_function:
                        self.messages.append(f"Line {i-1} should be empty between functions.")
                    previous_line_was_function = True
                elif not previous_line_was_function and not previous_line_was_import:
                    self.messages.append(f"Line {i} should be empty.")

        # Check if the last line is not empty
        if self.source_lines and self.source_lines[-1].strip() != '':
            self.messages.append("File should end with an empty line.")

    def check_first_line_empty(self):
        if not self.source_lines:
            return
        if self.source_lines[0].strip() == '':
            self.messages.append("The first line is empty.")
    
    def check_case_conventions(self):
        lower_camel_case_pattern = re.compile(r'^[a-z]+([A-Z][a-z0-9]*)*$')
        upper_camel_case_pattern = re.compile(r'^[A-Z]([A-Z0-9]*[a-z][a-z0-9]*[A-Z]|[a-z0-9]*[A-Z][A-Z0-9]*[a-z])[A-Za-z0-9]*$')

        def is_lower_camel_case(name):
            return bool(lower_camel_case_pattern.match(name))

        def is_upper_camel_case(name):
            return bool(upper_camel_case_pattern.match(name))

        for i, line in enumerate(self.source_lines, start=1):
            stripped_line = line.strip()
            if stripped_line.startswith('def '):
                method_name = stripped_line.split()[1].split('(')[0]
                if not is_lower_camel_case(method_name):
                    self.messages.append(f"Line {i}: Method '{method_name}' should use lower camel case.")

            if stripped_line.startswith('class '):
                class_name = stripped_line.split()[1].split('(')[0]
                if not is_upper_camel_case(class_name):
                    self.messages.append(f"Line {i}: Class '{class_name}' should use upper camel case.")
        
    def check_line_length(self):
        max_length = 100
        for i, line in enumerate(self.source_lines, start=1):
            if len(line) > max_length:
                self.messages.append(f"Line {i} exceeds the maximum line length of {max_length} characters.")

    def remove_unused_code(self):
        updated_lines = self.source_lines.copy()
        tree = ast.parse(self.source_code)

        # Detect if a class is present
        contains_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))

        if contains_class:
            # Handle self attributes separately if a class is present
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_line = updated_lines[node.lineno - 1]
                    unused_args = set(self.function_args.get(node.name, [])) - self.used_names
                    if unused_args:
                        for arg in unused_args:
                            function_line = re.sub(r'\b' + re.escape(arg) + r'\b\s*,?\s*', '', function_line)
                        function_line = re.sub(r',\s*\)', ')', function_line)  # Remove trailing commas
                        function_line = re.sub(r'\(\s*,', '(', function_line)  # Remove leading commas
                        updated_lines[node.lineno - 1] = function_line

            # Remove assignments of unused self attributes
            for class_name, attrs in self.class_attributes.items():
                unused_attrs = attrs - self.used_class_attributes
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self' and target.attr in unused_attrs:
                                updated_lines[node.lineno - 1] = ''

            # Remove extra blank lines around removed lines
            updated_lines = self.remove_extra_blank_lines(updated_lines)

        else:
            # Normal procedure for removing unused function arguments and variables
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_line = updated_lines[node.lineno - 1]
                    unused_args = set(self.function_args.get(node.name, [])) - self.used_names
                    if unused_args:
                        for arg in unused_args:
                            function_line = re.sub(r'\b' + re.escape(arg) + r'\b\s*,?\s*', '', function_line)
                        function_line = re.sub(r',\s*\)', ')', function_line)  # Remove trailing commas
                        function_line = re.sub(r'\(\s*,', '(', function_line)  # Remove leading commas
                        updated_lines[node.lineno - 1] = function_line

                # Remove assignments of unused variables
                if isinstance(node, ast.Assign):
                    assigned_vars = {target.id for target in node.targets if isinstance(target, ast.Name)}
                    if assigned_vars.issubset(self.unused_variables):
                        updated_lines[node.lineno - 1] = ''

        # Remove lines with unused imports
        for i, line in enumerate(updated_lines):
            if line.strip().startswith(('import ', 'from ')):
                parts = line.split()
                if len(parts) < 2:
                    continue  # Skip lines that don't match expected format
                if parts[0] == 'import':
                    import_name = parts[1]
                elif parts[0] == 'from' and len(parts) >= 4:
                    import_name = f"{parts[1]}.{parts[3]}"
                else:
                    continue  # Skip lines that don't match expected format
                
                if import_name in self.unused_imports:
                    updated_lines[i] = ''  # Remove the entire line

        # Apply formatting for blank lines
        formatted_lines = self.ensure_blank_lines_between_functions(updated_lines)

        self.source_lines = formatted_lines
        self.source_code = "\n".join(self.source_lines).strip()
        self.reorder_imports()
        
        return self.source_code
    
    def remove_extra_blank_lines(self, lines):
        result = []
        skip_next = False
        for i, line in enumerate(lines):
            if line.strip() == "":
                if skip_next or i == 0 or i == len(lines) - 1 or (i + 1 < len(lines) and lines[i + 1].strip() == ""):
                    continue
                skip_next = True
            else:
                skip_next = False
            result.append(line)
        return result

    def ensure_blank_lines_between_functions(self, lines):
        formatted_lines = []
        last_line_was_import = False
        last_line_was_func_or_class = False

        for i, line in enumerate(lines):
            stripped_line = line.strip()

            if stripped_line == "":
                if last_line_was_import or last_line_was_func_or_class:
                    # Avoid appending too many blank lines after imports or functions
                    continue

            if stripped_line.startswith(('def ', 'class ')):
                if last_line_was_import or (formatted_lines and formatted_lines[-1].strip() != ""):
                    # Ensure exactly one blank line before functions
                    if formatted_lines and formatted_lines[-1].strip() == "":
                        formatted_lines.pop()
                    formatted_lines.append("")
                last_line_was_func_or_class = True
                last_line_was_import = False
            elif stripped_line.startswith(('import ', 'from ')):
                last_line_was_import = True
                last_line_was_func_or_class = False
            else:
                last_line_was_func_or_class = False
                last_line_was_import = False

            formatted_lines.append(line)

        # Remove any leading or trailing blank lines
        while formatted_lines and formatted_lines[0].strip() == "":
            formatted_lines.pop(0)
        while formatted_lines and formatted_lines[-1].strip() == "":
            formatted_lines.pop()

        return formatted_lines

    def reorder_imports(self):
        stdlib_imports, third_party_imports, local_imports = [], [], []
        for line in self.source_lines:
            if line.startswith(('import ', 'from ')):
                if self.is_standard_library_import(line):
                    stdlib_imports.append(line)
                elif self.is_third_party_import(line):
                    third_party_imports.append(line)
                else:
                    local_imports.append(line)

        ordered_imports = (
            sorted(stdlib_imports) +
            ([""] if stdlib_imports and third_party_imports else []) +
            sorted(third_party_imports) +
            ([""] if third_party_imports and local_imports else []) +
            sorted(local_imports)
        )

        non_import_lines = [line for line in self.source_lines if not line.strip().startswith(('import ', 'from '))]
        
        self.source_lines = ordered_imports + [''] + non_import_lines
        self.source_code = "\n".join(self.source_lines).strip()
        return self.source_code

    def is_standard_library_import(self, import_line):
        stdlib_module_names = set(sys.stdlib_module_names)
        for module in stdlib_module_names:
            if import_line.startswith(f'import {module}') or import_line.startswith(f'from {module}'):
                return True
        return False

    def is_third_party_import(self, import_line):
        return not self.is_standard_library_import(import_line) and not self.is_local_import(import_line)

    def is_local_import(self, import_line):
        return 'local_module' in import_line  # Assuming 'local_module' is a placeholder for actual local module names

    def lint(self):
        tree = ast.parse(self.source_code)
        self.visit(tree)
        self.check_import_order()
        self.check_trailing_whitespace()
        self.check_unused_imports()
        self.check_unused_function_args()
        self.check_unused_variables()
        self.check_first_line_empty()
        self.check_empty_lines()
        self.check_case_conventions()
        self.check_line_length()
        return self.messages
    
    def fix(self):
        self.lint()  # Ensure all checks are run and data is populated
        self.source_code = self.remove_unused_code()  # Fix the code and update source_code

# Example usage
source_code = """
class MyClass:
    def __init__(self):
        self.used_attr = 10
        self.unused_attr = 20
    
    def method(self):
        return self.used_attr
"""

linter = JayLinter(source_code)
fixed_code = linter.fix()
print("Fixed code:\n", fixed_code)
