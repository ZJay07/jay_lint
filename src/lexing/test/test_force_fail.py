import unittest
from src.lexing.logic.lexing import JayLinter

class TestJayLinterFix(unittest.TestCase):
    def fix_code(self, code):
        linter = JayLinter(source_code=code)
        linter.fix()
        return linter.remove_unused_code()
    
    def force_fail(self):
        self.assertEqual(1, 2)
