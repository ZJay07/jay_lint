import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

from src.cli import main


def run_cli(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main(list(argv))
    return code, out.getvalue()


class TestTsCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def write(self, name, content):
        path = os.path.join(self.dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        return path

    def read(self, path):
        with open(path, encoding='utf-8', newline='') as f:
            return f.read()

    def test_lints_a_tsx_file(self):
        path = self.write('a.tsx', "import x from 'x';\n")
        code, out = run_cli(path)
        self.assertIn("Linting results:", out)
        self.assertIn("- Line 1: Import 'x' is not used.", out)
        self.assertEqual(code, 0)

    def test_clean_file_reports_no_issues(self):
        path = self.write('a.ts', "export const a = 1;\n")
        code, out = run_cli(path)
        self.assertIn("No issues found.", out)
        self.assertEqual(code, 0)

    def test_strict_exits_one_when_there_are_issues(self):
        path = self.write('a.ts', "import x from 'x';\n")
        self.assertEqual(run_cli('--strict', path)[0], 1)

    def test_strict_exits_zero_when_clean(self):
        path = self.write('a.ts', "export const a = 1;\n")
        self.assertEqual(run_cli('--strict', path)[0], 0)

    def test_fix_rewrites_the_file(self):
        path = self.write('a.ts', "import x from 'x';\nexport const a = 1;   \n")
        code, out = run_cli('--fix', path)
        self.assertEqual(self.read(path), "export const a = 1;\n")
        self.assertIn(f"Fixed and saved the file: {path}", out)
        self.assertEqual(code, 0)

    def test_fix_keeps_crlf_files_crlf(self):
        path = self.write('a.ts', "export const a = 1;  \r\n")
        run_cli('--fix', path)
        self.assertEqual(self.read(path), "export const a = 1;\r\n")

    def test_max_line_length_option(self):
        path = self.write('a.ts', "const total = firstValue + secondValue + thirdValue;\n")
        self.assertIn("exceeds the maximum line length of 20", run_cli('--max-line-length', '20', path)[1])
        self.assertIn("No issues found.", run_cli('--max-line-length', '200', path)[1])

    def test_directory_is_searched_recursively(self):
        self.write('src/a.tsx', "import x from 'x';\n")
        self.write('src/deep/b.ts', "import y from 'y';\n")
        _, out = run_cli(self.dir)
        self.assertIn("a.tsx", out)
        self.assertIn("b.ts", out)

    def test_directory_skips_node_modules_and_build_output(self):
        self.write('node_modules/pkg/a.ts', "import x from 'x';\n")
        self.write('.next/b.ts', "import x from 'x';\n")
        self.write('plz-out/c.ts', "import x from 'x';\n")
        _, out = run_cli(self.dir)
        self.assertNotIn("Import 'x'", out)

    def test_multiple_files_get_a_header_each(self):
        a = self.write('a.ts', "import x from 'x';\n")
        b = self.write('b.ts', "export const b = 1;\n")
        _, out = run_cli(a, b)
        self.assertIn(a, out)
        self.assertIn(b, out)

    def test_strict_fails_if_any_file_has_issues(self):
        a = self.write('a.ts', "import x from 'x';\n")
        b = self.write('b.ts', "export const b = 1;\n")
        self.assertEqual(run_cli('--strict', a, b)[0], 1)

    def test_missing_file_is_an_error(self):
        code, out = run_cli(os.path.join(self.dir, 'nope.ts'))
        self.assertIn("not found", out)

    def test_unsupported_extension_is_an_error(self):
        path = self.write('a.txt', "hello\n")
        self.assertIn("not a supported file", run_cli(path)[1])

    def test_help_uses_the_jlint_command_name(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            main(['--help'])
        self.assertIn("usage: jlint", out.getvalue())

    def test_missing_tree_sitter_gives_an_install_hint(self):
        path = self.write('a.ts', "export const a = 1;\n")
        # A None entry in sys.modules makes the import fail, like Python 3.7/3.8 where
        # the tree-sitter packages are not installed.
        with mock.patch.dict(sys.modules, {'src.lexing.logic.ts_linter': None}):
            code, out = run_cli('--strict', path)
        self.assertIn("needs Python 3.9 or newer", out)
        self.assertIn("pip install --upgrade jay_lint", out)
        self.assertEqual(code, 1)

    def test_python_files_still_use_the_python_linter(self):
        path = self.write('a.py', "import os\n")
        _, out = run_cli(path)
        self.assertIn("Import 'os' on line 1 is not used", out)


if __name__ == '__main__':
    unittest.main()
