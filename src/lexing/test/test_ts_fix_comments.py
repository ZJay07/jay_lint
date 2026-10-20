import unittest

from src.lexing.logic.ts_linter import TsLinter


def fix(code, max_line_length=40):
    return TsLinter(code, max_line_length=max_line_length).fix()


class TestTsFixLongComments(unittest.TestCase):
    def test_wraps_a_long_line_comment(self):
        code = "// aaaa bbbb cccc dddd eeee ffff gggg hhhh iiii jjjj kkkk\n"
        self.assertEqual(
            fix(code),
            "// aaaa bbbb cccc dddd eeee ffff gggg\n// hhhh iiii jjjj kkkk\n",
        )

    def test_keeps_indentation(self):
        code = "function f() {\n    // aaaa bbbb cccc dddd eeee ffff gggg hhhh iiii\n}\n"
        self.assertEqual(
            fix(code),
            "function f() {\n    // aaaa bbbb cccc dddd eeee ffff\n    // gggg hhhh iiii\n}\n",
        )

    def test_wraps_a_jsdoc_continuation_line(self):
        code = "/**\n * aaaa bbbb cccc dddd eeee ffff gggg hhhh iiii jjjj\n */\n"
        self.assertEqual(
            fix(code),
            "/**\n * aaaa bbbb cccc dddd eeee ffff gggg\n * hhhh iiii jjjj\n */\n",
        )

    def test_every_wrapped_line_fits(self):
        code = "// " + " ".join(["word"] * 30) + "\n"
        for line in fix(code).splitlines():
            self.assertLessEqual(len(line), 40)

    def test_a_word_longer_than_the_limit_is_kept_whole(self):
        long_word = "x" * 60
        self.assertEqual(fix(f"// aa {long_word} bb\n"), f"// aa\n// {long_word}\n// bb\n")

    def test_short_comments_are_left_alone(self):
        code = "// short comment\n"
        self.assertEqual(fix(code), code)

    def test_comment_without_a_space_after_slashes_keeps_that_style(self):
        code = "//aaaa bbbb cccc dddd eeee ffff gggg hhhh iiii jjjj\n"
        self.assertEqual(
            fix(code),
            "//aaaa bbbb cccc dddd eeee ffff gggg\n//hhhh iiii jjjj\n",
        )

    def test_comment_with_a_url_is_left_alone(self):
        code = "// see https://example.com/a/very/long/path/that/goes/past/the/limit\n"
        self.assertEqual(fix(code), code)

    def test_directive_comments_are_left_alone(self):
        for code in (
            "// eslint-disable-next-line some-very-long-rule-name another-rule-name\n",
            "// @ts-expect-error this explanation is much longer than the limit allows\n",
            "// prettier-ignore this explanation is much longer than the limit allows\n",
            "/// <reference path=\"a/very/long/path/that/goes/past/the/limit.d.ts\" />\n",
        ):
            self.assertEqual(fix(code), code)

    def test_comment_with_aligned_columns_is_left_alone(self):
        code = "// name    kind    notes    aaaa    bbbb    cccc    dddd    eeee\n"
        self.assertEqual(fix(code), code)

    def test_trailing_comments_are_left_alone(self):
        code = "const a = 1; // a very long trailing comment past the limit of forty\n"
        self.assertEqual(fix(code), code)

    def test_block_comment_first_line_is_left_alone(self):
        code = "/* aaaa bbbb cccc dddd eeee ffff gggg hhhh iiii jjjj kkkk */\n"
        self.assertEqual(fix(code), code)

    def test_comment_markers_inside_strings_are_not_touched(self):
        code = "const a = '// aaaa bbbb cccc dddd eeee ffff gggg hhhh iiii jjjj';\n"
        self.assertEqual(fix(code), code)

    def test_is_idempotent(self):
        code = "// " + " ".join(["word"] * 30) + "\n"
        once = fix(code)
        self.assertEqual(fix(once), once)

    def test_output_has_no_line_length_messages(self):
        code = "// " + " ".join(["word"] * 30) + "\n/**\n * " + " ".join(["word"] * 30) + "\n */\n"
        self.assertEqual(TsLinter(fix(code), max_line_length=40).lint(), [])

    def test_crlf_is_preserved(self):
        code = "// aaaa bbbb cccc dddd eeee ffff gggg hhhh iiii jjjj kkkk\r\n"
        self.assertEqual(
            fix(code),
            "// aaaa bbbb cccc dddd eeee ffff gggg\r\n// hhhh iiii jjjj kkkk\r\n",
        )


if __name__ == '__main__':
    unittest.main()
