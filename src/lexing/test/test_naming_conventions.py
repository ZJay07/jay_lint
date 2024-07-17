import unittest
from src.lexing.logic.lexing import JayLinter

class TestFunctionCommentLinter(unittest.TestCase):
    def lint_code(self, code):
        linter = JayLinter(source_code=code)
        return linter.lint()

    def test_case_conventions_class(self):
        code = """
class myClass:
    pass
class MySecondClass:
    pass
    """
        message = self.lint_code(code)
        self.assertIn("Line 2: Class 'myClass:' should use upper camel case.", message)

    def test_case_conventions_function(self):
        code = """
def myMethod():
    pass
def mySecond_method():
    pass
    """
        message = self.lint_code(code)
        self.assertIn("Line 4: Method 'mySecond_method' should use lower camel case.", message)
