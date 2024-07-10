import unittest
from src.lexing.logic.lexing import JayLinter

class TestFunctionWhiteSpaceLinter(unittest.TestCase):
    def lint_code(self, code):
        linter = JayLinter(source_code=code)
        return linter.lint()

    def test_trailing_whitespace(self):
        code = """
a = 1 
        """
        messages = self.lint_code(code)
        self.assertIn("Line 2 has trailing whitespace.", messages)

    def test_empty_line(self):
        code = """
a = 1

b = 2
        """
        messages = self.lint_code(code)
        self.assertIn("Line 3 is empty.", messages)

    def test_empty_line_between_functions(self):
        code = """
def func1():
    pass
def func2():
    pass
        """
        messages = self.lint_code(code)
        self.assertIn("Line 3 should be empty.", messages)

    def test_empty_line_between_imports_and_code(self):
        code = """
import a
a = 1
        """
        messages = self.lint_code(code)
        self.assertIn("Line 2 should be empty.", messages)

    def test_empty_line_at_end_of_file(self):
        code = """
def func1():
    pass"""
        messages = self.lint_code(code)
        self.assertIn("File should end with an empty line.", messages)