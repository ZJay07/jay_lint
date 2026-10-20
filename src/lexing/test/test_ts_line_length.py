import unittest

from src.lexing.logic.ts_linter import TsLinter


class TestTsLineLength(unittest.TestCase):
    def lint_code(self, code, max_line_length=40):
        return TsLinter(code, max_line_length=max_line_length).lint()

    def test_short_lines_are_fine(self):
        self.assertEqual(self.lint_code("const a = 1;\n"), [])

    def test_long_code_line_is_reported(self):
        code = "const total = firstValue + secondValue + thirdValue + fourthValue;\n"
        self.assertIn(
            "Line 1: Line exceeds the maximum line length of 40 characters.",
            self.lint_code(code),
        )

    def test_long_string_line_is_ignored(self):
        code = "const text = 'a very long string literal that goes past the limit';\n"
        self.assertEqual(self.lint_code(code), [])

    def test_long_template_literal_is_ignored(self):
        code = "const text = `a very long template literal that goes past the limit`;\n"
        self.assertEqual(self.lint_code(code), [])

    def test_long_comment_is_ignored(self):
        code = "// a very long comment that goes past the limit of forty chars\n"
        self.assertEqual(self.lint_code(code), [])

    def test_long_url_line_is_ignored(self):
        code = "// see https://example.com/a/very/long/path/that/goes/past/the/limit\n"
        self.assertEqual(self.lint_code(code), [])

    def test_long_jsx_attribute_string_is_ignored(self):
        code = 'const a = <div className="some very long class name list here" />;\n'
        self.assertEqual(self.lint_code(code), [])

    def test_line_numbers_are_correct(self):
        code = "const a = 1;\nconst total = firstValue + secondValue + thirdValue + 4;\n"
        messages = self.lint_code(code)
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].startswith("Line 2:"))


if __name__ == '__main__':
    unittest.main()
