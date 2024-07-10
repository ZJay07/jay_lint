import unittest
from src.lexing.logic.lexing import JayLinter

class TestFunctionVariablesLinter(unittest.TestCase):
    def lint_code(self, code):
        linter = JayLinter(source_code=code)
        return linter.lint()
    
    def test_unused_function_arg(self):
        code = """
def func_with_unused_arg(a, b):
    return a
        """
        messages = self.lint_code(code)
        self.assertIn("Function 'func_with_unused_arg' has an unused argument 'b'.", messages)

    def test_unused_variable(self):
        code = """
def func_with_unused_var(a):
    unused_var = 5
    return a
        """
        messages = self.lint_code(code)
        self.assertIn("Variable 'unused_var' assigned on line 3 is not used.", messages)
