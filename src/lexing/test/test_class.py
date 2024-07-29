import unittest
from src.lexing.logic.lexing import JayLinter

class TestJayLinterRemoveUnusedSelfAttributes(unittest.TestCase):
    def fix_and_remove_unused_self(self, code):
        linter = JayLinter(source_code=code)
        fixed_code = linter.remove_unused_code()
        return fixed_code.strip()

    def test_remove_unused_self_attribute(self):
        code = """
class MyClass:
    def __init__(self):
        self.used_attr = 10
        self.unused_attr = 20

    def method(self):
        return self.used_attr
"""
        expected_fixed_code = """
class MyClass:
    def __init__(self):
        self.used_attr = 10

    def method(self):
        return self.used_attr
"""
        fixed_code = self.fix_and_remove_unused_self(code)
        print(f"fixed_code: {fixed_code}")
        print(f"expected_fixed_code: {expected_fixed_code})")
        self.assertEqual(fixed_code, expected_fixed_code.strip())

    def test_remove_unused_self_attribute_with_comment(self):
        code = """
class MyClass:
    def __init__(self):
        self.used_attr = 10
        # This is a comment
        self.unused_attr = 20

    def method(self):
        return self.used_attr
"""
        expected_fixed_code = """
class MyClass:

    def __init__(self):
        self.used_attr = 10
        # This is a comment


    def method(self):
        return self.used_attr
"""
        fixed_code = self.fix_and_remove_unused_self(code)
        print(f"fixed_code: {fixed_code}")
        print(f"expected_fixed_code: {expected_fixed_code})")
        self.assertEqual(fixed_code, expected_fixed_code.strip())

    def test_no_removal_for_used_self_attribute(self):
        code = """
class MyClass:
    def __init__(self):
        self.used_attr = 10

    def method(self):
        return self.used_attr
"""
        expected_fixed_code = code.strip()
        fixed_code = self.fix_and_remove_unused_self(code)
        print(f"fixed_code: {fixed_code}")
        print(f"expected_fixed_code: {expected_fixed_code})")
        self.assertEqual(fixed_code, expected_fixed_code)

if __name__ == '__main__':
    unittest.main()
