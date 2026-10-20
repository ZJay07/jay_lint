import unittest

from src.lexing.logic.ts_linter import TsLinter


def lint(code):
    return TsLinter(code).lint()


class TestTsImportOrder(unittest.TestCase):
    def test_correct_order_has_no_messages(self):
        code = (
            "import { motion } from 'framer-motion';\n"
            "\n"
            "import { fadeIn } from '@/utils/motion';\n"
            "\n"
            "import SectionWrapper from './SectionWrapper';\n"
            "\n"
            "console.log(motion, fadeIn, SectionWrapper);\n"
        )
        self.assertEqual(lint(code), [])

    def test_sibling_before_internal_is_reported(self):
        # The order that broke the Vercel build: ./sibling above the @/ alias.
        code = (
            "import { motion } from 'framer-motion';\n"
            "\n"
            "import SectionWrapper from './SectionWrapper';\n"
            "\n"
            "import { fadeIn } from '@/utils/motion';\n"
            "\n"
            "console.log(motion, fadeIn, SectionWrapper);\n"
        )
        self.assertIn(
            "Line 5: '@/utils/motion' import should occur before import of './SectionWrapper'.",
            lint(code),
        )

    def test_unsorted_within_a_group_is_reported(self):
        code = (
            "import b from 'beta';\n"
            "import a from 'alpha';\n"
            "\n"
            "console.log(a, b);\n"
        )
        self.assertIn("Line 2: 'alpha' import should occur before import of 'beta'.", lint(code))

    def test_alphabetize_ignores_case(self):
        code = "import a from 'Alpha';\nimport b from 'beta';\n\nconsole.log(a, b);\n"
        self.assertEqual(lint(code), [])

    def test_missing_blank_line_between_groups_is_reported(self):
        code = (
            "import a from 'alpha';\n"
            "import b from './b';\n"
            "\n"
            "console.log(a, b);\n"
        )
        self.assertIn("Line 2: There should be a blank line between import groups.", lint(code))

    def test_blank_line_inside_a_group_is_reported(self):
        code = "import a from 'alpha';\n\nimport b from 'beta';\n\nconsole.log(a, b);\n"
        self.assertIn("Line 3: There should be no blank line within an import group.", lint(code))

    def test_parent_comes_before_sibling(self):
        code = (
            "import a from '../a';\n"
            "\n"
            "import b from './b';\n"
            "\n"
            "console.log(a, b);\n"
        )
        self.assertEqual(lint(code), [])

    def test_side_effect_imports_are_ignored_for_ordering(self):
        code = (
            "import './globals.css';\n"
            "import { motion } from 'framer-motion';\n"
            "\n"
            "console.log(motion);\n"
        )
        self.assertEqual(lint(code), [])

    def test_node_builtins_come_first(self):
        code = "import fs from 'fs';\n\nimport a from 'alpha';\n\nconsole.log(fs, a);\n"
        self.assertEqual(lint(code), [])


if __name__ == '__main__':
    unittest.main()
