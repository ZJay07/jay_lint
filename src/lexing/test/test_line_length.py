import unittest
from src.lexing.logic.lexing import JayLinter

class TestLineLength(unittest.TestCase):
    def lint_code(self, code):
        linter = JayLinter(source_code=code)
        return linter.lint()
    
    def test_valid_line_length(self):
        code = """
class myClass:
    def __init__(self):
        pass
    """
        message = self.lint_code(code)
        for i, message in enumerate(message):
            self.assertNotIn(f"Line {i} exceeds the maximum line length of 100 characters.", message)
    
    def test_invalid_line_length(self):
        code = """
class myClass:
    def __init__(self):
        self.thisIsAVeryLongVariableNameJUSTAPPENDINGEXTRALINES = 3.1421234566778891991919191919919113213123
    """
        message = self.lint_code(code)
        self.assertIn("Line 4 exceeds the maximum line length of 100 characters.", message)
