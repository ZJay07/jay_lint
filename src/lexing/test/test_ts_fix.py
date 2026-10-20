import unittest

from src.lexing.logic.ts_linter import TsLinter


def fix(code):
    return TsLinter(code).fix()


class TestTsFixUnusedImports(unittest.TestCase):
    def test_removes_whole_unused_import(self):
        code = "import React from 'react';\nimport a from 'alpha';\n\nconsole.log(a);\n"
        self.assertEqual(fix(code), "import a from 'alpha';\n\nconsole.log(a);\n")

    def test_removes_only_unused_named_specifier(self):
        code = "import { a, b } from 'lib';\n\nconsole.log(a);\n"
        self.assertEqual(fix(code), "import { a } from 'lib';\n\nconsole.log(a);\n")

    def test_keeps_default_when_only_named_is_unused(self):
        code = "import d, { a } from 'lib';\n\nconsole.log(d);\n"
        self.assertEqual(fix(code), "import d from 'lib';\n\nconsole.log(d);\n")

    def test_keeps_alias_syntax(self):
        code = "import { a as x, b as y } from 'lib';\n\nconsole.log(x);\n"
        self.assertEqual(fix(code), "import { a as x } from 'lib';\n\nconsole.log(x);\n")

    def test_collapses_multiline_import_that_changes(self):
        code = "import {\n  a,\n  b,\n} from 'lib';\n\nconsole.log(a);\n"
        self.assertEqual(fix(code), "import { a } from 'lib';\n\nconsole.log(a);\n")

    def test_leaves_untouched_import_formatting_alone(self):
        code = "import {\n  a,\n  b,\n} from 'lib';\n\nconsole.log(a, b);\n"
        self.assertEqual(fix(code), code)

    def test_preserves_quote_style_and_missing_semicolon(self):
        code = 'import { a, b } from "lib"\n\nconsole.log(a)\n'
        self.assertEqual(fix(code), 'import { a } from "lib"\n\nconsole.log(a)\n')

    def test_never_removes_side_effect_imports(self):
        code = "import './globals.css';\n"
        self.assertEqual(fix(code), code)

    def test_keeps_type_modifier(self):
        code = "import type { A, B } from './types';\n\nconst x: A = 1;\n"
        self.assertEqual(fix(code), "import type { A } from './types';\n\nconst x: A = 1;\n")


class TestTsFixWhitespace(unittest.TestCase):
    def test_strips_trailing_whitespace(self):
        self.assertEqual(fix("const a = 1;   \n"), "const a = 1;\n")

    def test_collapses_consecutive_blank_lines(self):
        self.assertEqual(fix("const a = 1;\n\n\n\nconst b = 2;\n"), "const a = 1;\n\nconst b = 2;\n")

    def test_removes_leading_blank_lines(self):
        self.assertEqual(fix("\n\nconst a = 1;\n"), "const a = 1;\n")

    def test_adds_missing_final_newline(self):
        self.assertEqual(fix("const a = 1;"), "const a = 1;\n")

    def test_collapses_extra_blank_lines_at_end(self):
        self.assertEqual(fix("const a = 1;\n\n\n"), "const a = 1;\n")

    def test_template_literal_content_is_untouched(self):
        code = "const a = `one   \n\n\ntwo`;\n"
        self.assertEqual(fix(code), code)

    def test_crlf_line_endings_are_preserved(self):
        self.assertEqual(fix("const a = 1;  \r\nconst b = 2;\r\n"), "const a = 1;\r\nconst b = 2;\r\n")

    def test_fix_output_lints_clean(self):
        code = "import x from 'x';\n\n\nconst a = 1;   \n\n\n"
        self.assertEqual(TsLinter(fix(code)).lint(), [])


if __name__ == '__main__':
    unittest.main()
