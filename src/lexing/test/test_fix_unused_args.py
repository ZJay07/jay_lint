import unittest
from src.lexing.logic.lexing import JayLinter

class TestJayLinterFix(unittest.TestCase):
    def fix_code(self, code):
        linter = JayLinter(source_code=code)
        linter.fix()
        return linter.remove_unused_code()

    def test_fix_removes_unused_imports(self):
        code = """
import os
import sys

def my_function():
    return "Hello, World!"
"""
        expected_fixed_code = """
def my_function():
    return "Hello, World!"
"""
        fixed_code = self.fix_code(code)
        self.assertEqual(fixed_code.strip(), expected_fixed_code.strip())

    def test_fix_removes_unused_variables(self):
        code = """
def my_function():
    x = 42
    y = "unused"
    return x
"""
        expected_fixed_code = """
def my_function():
    x = 42
    return x
"""
        fixed_code = self.fix_code(code)
        self.assertEqual(fixed_code.strip(), expected_fixed_code.strip())

    def test_fix_removes_unused_function_arguments(self):
        code = """
def my_function(unused_arg, used_arg):
    return used_arg
"""
        expected_fixed_code = """
def my_function(used_arg):
    return used_arg
"""
        fixed_code = self.fix_code(code)
        self.assertEqual(fixed_code.strip(), expected_fixed_code.strip())
    
    def test_fix_removes_unused_variables_3_variables(self):
        code = """
def my_function():
    x = 42
    y = "used"
    z = "unused"
    return x + y
"""
        expected_fixed_code = """
def my_function():
    x = 42
    y = "used"
    return x + y
"""
        fixed_code = self.fix_code(code)
        print(f"fixed_code: {fixed_code}")
        print(f"expected_fixed_code: {expected_fixed_code}")
        self.assertEqual(fixed_code.strip(), expected_fixed_code.strip())
    
    def test_fix_removes_unused_variables_3_variables_middle(self):
        code = """
def my_function():
    x = 42
    y = "unused"
    z = "used"
    return x + z
"""
        expected_fixed_code = """
def my_function():
    x = 42
    z = "used"
    return x + z
"""
        fixed_code = self.fix_code(code)
        print(f"fixed_code: {fixed_code}")
        print(f"expected_fixed_code: {expected_fixed_code}")
        self.assertEqual(fixed_code.strip(), expected_fixed_code.strip())

if __name__ == '__main__':
    unittest.main()
