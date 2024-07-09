import unittest
import ast
from src.lexing.logic.lexing import FunctionArgLinter

class TestFunctionArgLinter(unittest.TestCase):
    # Test data for different scenarios
    TEST_DATA_COMMENT = [
        ("""
# This is a comment
def function_with_comment():
    pass
""", True),  # This should pass the comment check
        ("""
def function_without_comment():
    pass
""", False)  # This should fail the comment check
    ]

    TEST_DATA_ARGS = [
        ("def function_few_args(a, b): pass", True),  # This should pass the args check
        ("def function_too_many_args(a, b, c, d, e, f): pass", False)  # This should fail the args check
    ]

    TEST_DATA_UNUSED_ARGS = [
        ("""
def function_with_unused_arg(a, b):
    return b
""", False),  # This should fail because 'a' is unused
        ("""
def function_with_all_used_args(a, b):
    return a + b
""", True)  # This should pass because all arguments are used
    ]

    TEST_DATA_UNUSED_IMPORTS = [
        ("""
import os

def function_using_os():
    print(os.name)
""", True),  # This should pass because 'os' is used
        ("""
import sys

def function_not_using_sys():
    pass
""", False)  # This should fail because 'sys' is not used
    ]

    TEST_DATA_IMPORT_ORDER = [
        ("""
import os
import sys
import json
import ast
""", False),  # This should fail the import order check
        ("""
import ast
import json
import os
import sys
""", True)  # This should pass the import order check
    ]

    def test_function_comment(self):
        for source_code, expected in self.TEST_DATA_COMMENT:
            source_lines = source_code.splitlines()
            linter = FunctionArgLinter(max_args=4, source_lines=source_lines)
            tree = ast.parse(source_code)
            linter.visit(tree)
            if expected:
                self.assertFalse(any("lacks a preceding comment" in msg for msg in linter.messages), "Expected a comment, but none was found.")
            else:
                self.assertTrue(any("lacks a preceding comment" in msg for msg in linter.messages), "Expected no comment, but one was found.")

    def test_function_args(self):
        for source_code, expected in self.TEST_DATA_ARGS:
            source_lines = source_code.splitlines()
            linter = FunctionArgLinter(max_args=4, source_lines=source_lines)
            tree = ast.parse(source_code)
            linter.visit(tree)
            if expected:
                self.assertFalse(any("has too many arguments" in msg for msg in linter.messages), "Expected fewer arguments, but found too many.")
            else:
                self.assertTrue(any("has too many arguments" in msg for msg in linter.messages), "Expected too many arguments, but found fewer.")

    def test_unused_args(self):
        for source_code, expected in self.TEST_DATA_UNUSED_ARGS:
            source_lines = source_code.splitlines()
            linter = FunctionArgLinter(max_args=4, source_lines=source_lines)
            tree = ast.parse(source_code)
            linter.visit(tree)
            if expected:
                self.assertFalse(any("has an unused argument" in msg for msg in linter.messages), "Expected no unused arguments, but found some.")
            else:
                self.assertTrue(any("has an unused argument" in msg for msg in linter.messages), "Expected unused arguments, but found none.")

    def test_unused_imports(self):
        for source_code, expected in self.TEST_DATA_UNUSED_IMPORTS:
            source_lines = source_code.splitlines()
            linter = FunctionArgLinter(max_args=4, source_lines=source_lines)
            tree = ast.parse(source_code)
            linter.visit(tree)
            linter.finalize()
            if expected:
                self.assertFalse(any("is not used" in msg for msg in linter.messages), "Expected no unused imports, but found some.")
            else:
                self.assertTrue(any("is not used" in msg for msg in linter.messages), "Expected unused imports, but found none.")

    def test_import_order(self):
        for source_code, expected in self.TEST_DATA_IMPORT_ORDER:
            source_lines = source_code.strip().splitlines()
            linter = FunctionArgLinter(max_args=4, source_lines=source_lines)
            tree = ast.parse(source_code)
            linter.visit(tree)
            linter.finalize()
            self.assertEqual("Imports are not in lexicographical order." not in linter.messages, expected)

if __name__ == '__main__':
    unittest.main()
