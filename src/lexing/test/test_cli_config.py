import contextlib
import io
import os
import tempfile
import unittest

from src.cli import main


class TestCliConfig(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self._cwd = os.getcwd()
        self.addCleanup(os.chdir, self._cwd)

    def write(self, name, content):
        path = os.path.join(self.root, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        return path

    def run_cli(self, *argv, cwd=None):
        os.chdir(cwd or self.root)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(list(argv))
        return code, out.getvalue()

    def test_runs_the_paths_from_jlint_toml_when_no_files_are_given(self):
        self.write('jlint.toml', 'paths = ["src"]\n')
        self.write('src/a.ts', "import x from 'x';\n")
        code, out = self.run_cli()
        self.assertIn("Import 'x' is not used.", out)

    def test_reads_tool_jlint_from_pyproject_toml(self):
        self.write('pyproject.toml', '[tool.jlint]\npaths = ["src"]\n')
        self.write('src/a.ts', "import x from 'x';\n")
        self.assertIn("Import 'x' is not used.", self.run_cli()[1])

    def test_jlint_toml_wins_over_pyproject_toml(self):
        self.write('jlint.toml', 'paths = ["one"]\n')
        self.write('pyproject.toml', '[tool.jlint]\npaths = ["two"]\n')
        self.write('one/a.ts', "import first from 'x';\n")
        self.write('two/b.ts', "import second from 'x';\n")
        out = self.run_cli()[1]
        self.assertIn("'first'", out)
        self.assertNotIn("'second'", out)

    def test_pyproject_without_a_jlint_table_is_ignored(self):
        self.write('pyproject.toml', '[tool.poetry]\nname = "x"\n')
        code, out = self.run_cli()
        self.assertNotEqual(code, 0)
        self.assertIn("No files given", out)

    def test_max_line_length_and_strict_come_from_the_config(self):
        self.write('jlint.toml', 'paths = ["src"]\nmax-line-length = 20\nstrict = true\n')
        self.write('src/a.ts', "const total = firstValue + secondValue;\n")
        code, out = self.run_cli()
        self.assertIn("maximum line length of 20", out)
        self.assertEqual(code, 1)

    def test_command_line_overrides_the_config(self):
        self.write('jlint.toml', 'paths = ["src"]\nmax-line-length = 20\n')
        self.write('src/a.ts', "const total = firstValue + secondValue;\n")
        self.assertIn("No issues found.", self.run_cli('--max-line-length', '200')[1])

    def test_files_on_the_command_line_override_config_paths(self):
        self.write('jlint.toml', 'paths = ["one"]\n')
        self.write('one/a.ts', "import first from 'x';\n")
        self.write('two/b.ts', "import second from 'x';\n")
        out = self.run_cli('two')[1]
        self.assertIn("'second'", out)
        self.assertNotIn("'first'", out)

    def test_config_is_found_in_a_parent_directory_and_paths_are_relative_to_it(self):
        self.write('jlint.toml', 'paths = ["src"]\n')
        self.write('src/a.ts', "import x from 'x';\n")
        sub = os.path.join(self.root, 'deep', 'er')
        os.makedirs(sub)
        self.assertIn("Import 'x' is not used.", self.run_cli(cwd=sub)[1])

    def test_exclude_skips_matching_paths(self):
        self.write('jlint.toml', 'paths = ["src"]\nexclude = ["generated"]\n')
        self.write('src/a.ts', "import first from 'x';\n")
        self.write('src/generated/b.ts', "import second from 'x';\n")
        out = self.run_cli()[1]
        self.assertIn("'first'", out)
        self.assertNotIn("'second'", out)

    def test_unknown_key_is_an_error(self):
        self.write('jlint.toml', 'paths = ["src"]\nmax_line_lenght = 88\n')
        code, out = self.run_cli()
        self.assertNotEqual(code, 0)
        self.assertIn("Unknown setting 'max_line_lenght'", out)

    def test_wrong_type_is_an_error(self):
        self.write('jlint.toml', 'paths = "src"\n')
        code, out = self.run_cli()
        self.assertNotEqual(code, 0)
        self.assertIn("'paths' must be a list of strings", out)

    def test_invalid_toml_is_an_error(self):
        self.write('jlint.toml', 'paths = [\n')
        code, out = self.run_cli()
        self.assertNotEqual(code, 0)
        self.assertIn("jlint.toml", out)

    def test_explicit_config_option(self):
        path = self.write('configs/mine.toml', 'paths = ["../src"]\n')
        self.write('src/a.ts', "import x from 'x';\n")
        self.assertIn("Import 'x' is not used.", self.run_cli('--config', path)[1])

    def test_missing_explicit_config_is_an_error(self):
        code, out = self.run_cli('--config', os.path.join(self.root, 'nope.toml'))
        self.assertNotEqual(code, 0)
        self.assertIn("not found", out)

    def test_no_files_and_no_config_is_an_error(self):
        code, out = self.run_cli()
        self.assertNotEqual(code, 0)
        self.assertIn("No files given", out)


if __name__ == '__main__':
    unittest.main()
