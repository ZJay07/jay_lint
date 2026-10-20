import unittest

from src.lexing.logic.ts_linter import TsLinter


def fix(code):
    return TsLinter(code).fix()


class TestTsFixImportOrder(unittest.TestCase):
    def test_moves_internal_alias_above_sibling(self):
        # The exact reordering ESLint's import/order asks for in this project.
        code = (
            "import { motion } from 'framer-motion';\n"
            "\n"
            "import SectionWrapper from './SectionWrapper';\n"
            "\n"
            "import { fadeIn } from '@/utils/motion';\n"
            "\n"
            "console.log(motion, fadeIn, SectionWrapper);\n"
        )
        expected = (
            "import { motion } from 'framer-motion';\n"
            "\n"
            "import { fadeIn } from '@/utils/motion';\n"
            "\n"
            "import SectionWrapper from './SectionWrapper';\n"
            "\n"
            "console.log(motion, fadeIn, SectionWrapper);\n"
        )
        self.assertEqual(fix(code), expected)

    def test_sorts_within_a_group(self):
        code = "import b from 'beta';\nimport a from 'alpha';\n\nconsole.log(a, b);\n"
        self.assertEqual(
            fix(code), "import a from 'alpha';\nimport b from 'beta';\n\nconsole.log(a, b);\n"
        )

    def test_inserts_blank_line_between_groups(self):
        code = "import a from 'alpha';\nimport b from './b';\n\nconsole.log(a, b);\n"
        self.assertEqual(
            fix(code), "import a from 'alpha';\n\nimport b from './b';\n\nconsole.log(a, b);\n"
        )

    def test_removes_blank_line_inside_a_group(self):
        code = "import a from 'alpha';\n\nimport b from 'beta';\n\nconsole.log(a, b);\n"
        self.assertEqual(
            fix(code), "import a from 'alpha';\nimport b from 'beta';\n\nconsole.log(a, b);\n"
        )

    def test_keeps_multiline_imports_intact(self):
        code = (
            "import b from './b';\n"
            "import {\n  x,\n  y,\n} from 'lib';\n"
            "\n"
            "console.log(b, x, y);\n"
        )
        expected = (
            "import {\n  x,\n  y,\n} from 'lib';\n"
            "\n"
            "import b from './b';\n"
            "\n"
            "console.log(b, x, y);\n"
        )
        self.assertEqual(fix(code), expected)

    def test_keeps_use_client_directive_first(self):
        code = (
            "'use client';\n"
            "\n"
            "import b from './b';\n"
            "import a from 'alpha';\n"
            "\n"
            "console.log(a, b);\n"
        )
        expected = (
            "'use client';\n"
            "\n"
            "import a from 'alpha';\n"
            "\n"
            "import b from './b';\n"
            "\n"
            "console.log(a, b);\n"
        )
        self.assertEqual(fix(code), expected)

    def test_side_effect_import_stays_in_place(self):
        code = (
            "import './globals.css';\n"
            "import b from 'beta';\n"
            "import a from 'alpha';\n"
            "\n"
            "console.log(a, b);\n"
        )
        expected = (
            "import './globals.css';\n"
            "import a from 'alpha';\n"
            "import b from 'beta';\n"
            "\n"
            "console.log(a, b);\n"
        )
        self.assertEqual(fix(code), expected)

    def test_leaves_imports_alone_when_a_comment_sits_between_them(self):
        code = (
            "import b from 'beta';\n"
            "// keep this note next to alpha\n"
            "import a from 'alpha';\n"
            "\n"
            "console.log(a, b);\n"
        )
        self.assertEqual(fix(code), code)

    def test_is_idempotent(self):
        code = "import b from './b';\nimport a from 'alpha';\n\nconsole.log(a, b);\n"
        once = fix(code)
        self.assertEqual(fix(once), once)

    def test_fixed_output_has_no_import_messages(self):
        code = "import b from './b';\nimport a from 'alpha';\n\nconsole.log(a, b);\n"
        self.assertEqual(TsLinter(fix(code)).lint(), [])

    def test_crlf_is_preserved(self):
        code = "import b from './b';\r\nimport a from 'alpha';\r\n\r\nconsole.log(a, b);\r\n"
        self.assertEqual(
            fix(code),
            "import a from 'alpha';\r\n\r\nimport b from './b';\r\n\r\nconsole.log(a, b);\r\n",
        )


if __name__ == '__main__':
    unittest.main()
