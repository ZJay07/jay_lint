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