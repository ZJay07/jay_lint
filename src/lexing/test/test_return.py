import unittest
from src.lexing.logic.lexing import JayLinter

class TestReturnLinter(unittest.TestCase):

    def lint_code(self, code):
        linter = JayLinter(source_code=code)
        return linter.lint()

    def test_return_with_blank_line_before(self):
        code = """
def function_with_blank_line():
    
    return "something"
        """
        messages = self.lint_code(code)
        self.assertIn("Line 4 has a blank line before 'return' statement.", messages)

    def test_return_without_blank_line_before(self):
        code = """
def function_without_blank_line():
    return "something"
        """
        messages = self.lint_code(code)
        self.assertNotIn("Line 4 has a blank line before 'return' statement.", messages)
    
    def fix_code(self, code):
        linter = JayLinter(source_code=code)
        linter.fix()
        return linter.source_code.strip()

    def test_fix_return_with_blank_line_before(self):
        code = """
def function_with_blank_line():

    return "something"
        """
        expected_fixed_code = """
def function_with_blank_line():
    return "something"
        """
        fixed_code = self.fix_code(code)
        self.assertEqual(fixed_code.strip(), expected_fixed_code.strip())

    def test_fix_return_without_blank_line_before(self):
        code = """
def function_without_blank_line():
    return "something"
        """
        expected_fixed_code = """
def function_without_blank_line():
    return "something"
        """
        fixed_code = self.fix_code(code)
        self.assertEqual(fixed_code.strip(), expected_fixed_code.strip())
    
    def test_fix_return_with_blank_line_before_variables(self):
        code = """
def function_with_blank_line():
    a = 1

    return a
        """
        expected_fixed_code = """
def function_with_blank_line():
    a = 1
    return a
        """
        fixed_code = self.fix_code(code)
        print(f"fixed_code: {fixed_code}")
        print(f"expected_fixed_code: {expected_fixed_code}")
        self.assertEqual(fixed_code.strip(), expected_fixed_code.strip())

if __name__ == '__main__':
    unittest.main()
