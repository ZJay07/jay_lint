import unittest
from src.lexing.logic.lexing import JayLinter

class TestJayLinterImportsAndUnusedArgs(unittest.TestCase):
    def lint_code(self, code):
        linter = JayLinter(source_code=code)
        return linter.lint()
    def lint_and_fix_code(self, code, unused_imports=None):
        linter = JayLinter(source_code=code)
        if unused_imports:
            linter.unused_imports = set(unused_imports)
        linter.fix()
        return linter.source_code.strip()

    def test_remove_unused_imports_and_reorder(self):
        code = """
import os
import sys
import json
from local_module import local_function

def hello(used):
    return used

def another_function(unused_param):
    pass
"""
        expected_fixed_code = """
def hello(used):
    return used

def another_function():
    pass
"""
        fixed_code = self.lint_and_fix_code(code, unused_imports=['os'])
        print ("fixed_code:", fixed_code)
        print ("expected_fixed_code:", expected_fixed_code.strip())
        print(self.lint_code(code))
        self.assertEqual(fixed_code, expected_fixed_code.strip())

    def test_remove_unused_function_arguments(self):
        code = """
import os
import sys

def hello(unused_arg, used_arg):
    os.path.join()
    return used_arg

def another_function(unused_param, used_param):
    return used_param
"""
        expected_fixed_code = """
import os

def hello(used_arg):
    os.path.join()
    return used_arg

def another_function(used_param):
    return used_param
"""
        fixed_code = self.lint_and_fix_code(code)
        print ("fixed_code:", fixed_code)
        print ("expected_fixed_code:", expected_fixed_code.strip())
        self.assertEqual(fixed_code, expected_fixed_code.strip())

    def test_mixed_imports_and_unused_args(self):
        code = """
import os
import sys
import thirdparty
from local_module import local_function

def mixed_func(unused_arg1, used_arg1, unused_arg2, used_arg2):
    thirdparty.some_function()
    return used_arg1 + used_arg2

def another_func():
    pass
"""
        expected_fixed_code = """
import thirdparty

def mixed_func(used_arg1, used_arg2):
    thirdparty.some_function()
    return used_arg1 + used_arg2

def another_func():
    pass
"""
        fixed_code = self.lint_and_fix_code(code, unused_imports=['os'])
        print ("fixed_code:", fixed_code)
        print ("expected_fixed_code:", expected_fixed_code.strip())
        self.assertEqual(fixed_code, expected_fixed_code.strip())

if __name__ == '__main__':
    unittest.main()
