import unittest
from src.lexing.logic.lexing import JayLinter

class TestFunctionImportLinter(unittest.TestCase):
    
    def lint_code(self, code):
        linter = JayLinter(source_code=code)
        return linter.lint()

    def test_import_order_correct(self):
        code = """
import a
import b
        """
        messages = self.lint_code(code)
        self.assertNotIn("Imports are not in lexicographical order.", messages)

    def test_import_order_incorrect(self):
        code = """
import b
import a
        """
        messages = self.lint_code(code)
        self.assertIn("Imports are not in lexicographical order.", messages)

    def test_import_from_order_correct(self):
        code = """
from b import x
from b import y
        """
        messages = self.lint_code(code)
        self.assertNotIn("Imports are not in lexicographical order.", messages)

    def test_import_from_order_incorrect(self):
        code = """
from b import y
from b import x
        """
        messages = self.lint_code(code)
        self.assertIn("Imports are not in lexicographical order.", messages)

if __name__ == '__main__':
    unittest.main()