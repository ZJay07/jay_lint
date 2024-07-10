import unittest
from src.lexing.logic.lexing import JayLinter

class TestFunctionCommentLinter(unittest.TestCase):

    def lint_code(self, code):
        linter = JayLinter(source_code=code)
        return linter.lint()

    def test_function_lacking_comment(self):
        code = """
def func_without_comment(a, b):
    pass
        """
        messages = self.lint_code(code)
        self.assertIn("Function 'func_without_comment' lacks a preceding comment.", messages)

    def test_function_with_comment(self):
        code = """
# This is a comment
def func_with_comment(a, b):
    pass
        """
        messages = self.lint_code(code)
        self.assertNotIn("Function 'func_with_comment' lacks a preceding comment.", messages)

if __name__ == '__main__':
    unittest.main()
