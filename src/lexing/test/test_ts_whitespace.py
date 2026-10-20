import unittest

from src.lexing.logic.ts_linter import TsLinter


class TestTsWhitespace(unittest.TestCase):
    def lint_code(self, code):
        return TsLinter(code).lint()

    def test_clean_file_has_no_messages(self):
        self.assertEqual(self.lint_code("const a = 1;\n"), [])

    def test_trailing_whitespace_is_reported(self):
        self.assertIn(
            "Line 1: Line has trailing whitespace.",
            self.lint_code("const a = 1;   \n"),
        )

    def test_trailing_whitespace_inside_template_literal_is_content(self):
        code = "const a = `line one   \nline two`;\n"
        self.assertEqual(self.lint_code(code), [])

    def test_two_blank_lines_in_a_row_are_reported(self):
        code = "const a = 1;\n\n\nconst b = 2;\n"
        self.assertIn(
            "Line 3: Line has more than one consecutive blank line.",
            self.lint_code(code),
        )

    def test_single_blank_line_is_fine(self):
        self.assertEqual(self.lint_code("const a = 1;\n\nconst b = 2;\n"), [])

    def test_blank_lines_inside_template_literal_are_content(self):
        code = "const a = `one\n\n\ntwo`;\n"
        self.assertEqual(self.lint_code(code), [])

    def test_first_line_empty_is_reported(self):
        self.assertIn("Line 1: The first line is empty.", self.lint_code("\nconst a = 1;\n"))

    def test_missing_final_newline_is_reported(self):
        self.assertIn(
            "Line 1: File should end with a newline.",
            self.lint_code("const a = 1;"),
        )

    def test_extra_blank_lines_at_end_are_reported(self):
        self.assertIn(
            "Line 3: File should end with a single newline.",
            self.lint_code("const a = 1;\n\n\n"),
        )


if __name__ == '__main__':
    unittest.main()
