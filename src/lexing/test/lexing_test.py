import unittest
from src.lexing.logic import lexing

class TestLexing(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(lexing.FunctionRules().hello_world(), None)