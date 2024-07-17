import unittest
from src.lexing.logic.lexing import JayLinter

class TestFunctionCommentLinter(unittest.TestCase):

    def lint_code(self, code):
        linter = JayLinter(source_code=code)
        linter.lint()
        return linter.fix()