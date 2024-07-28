import unittest
from src.lexing.logic.lexing import JayLinter

class TestJayLinterReorderImports(unittest.TestCase):
    def fix_and_reorder_code(self, code, unused_imports=None):
        linter = JayLinter(source_code=code)
        if unused_imports:
            linter.unused_imports = set(unused_imports)
        linter.remove_unused_code()  # This also calls reorder_imports internally
        return linter.source_code.strip()

    def test_reorder_imports_basic(self):
        code = """
import sys
import os
import thirdparty
from local import local_module

def my_function():
    return "Hello, World!"
"""
        expected_fixed_code = """
import os
import sys

import thirdparty

from local import local_module

def my_function():
    return "Hello, World!"
"""
        reordered_code = self.fix_and_reorder_code(code)
        print("reordered_code:", reordered_code)
        print("expected_fixed_code:", expected_fixed_code)
        self.assertEqual(reordered_code, expected_fixed_code.strip())

    def test_reorder_imports_with_unused(self):
        code = """
import os
import sys
import thirdparty
from local import local_module

def my_function():
    return "Hello, World!"
"""
        expected_fixed_code = """
import sys

import thirdparty

from local import local_module

def my_function():
    return "Hello, World!"
"""
        reordered_code = self.fix_and_reorder_code(code, unused_imports=['os'])
        self.assertEqual(reordered_code, expected_fixed_code.strip())

    def test_reorder_imports_with_local_first(self):
        code = """
from . import local_module
import os
import thirdparty
import sys

def my_function():
    return "Hello, World!"
"""
        expected_fixed_code = """
import os
import sys

import thirdparty

from . import local_module

def my_function():
    return "Hello, World!"
"""
        reordered_code = self.fix_and_reorder_code(code)
        self.assertEqual(reordered_code, expected_fixed_code.strip())

if __name__ == '__main__':
    unittest.main()
