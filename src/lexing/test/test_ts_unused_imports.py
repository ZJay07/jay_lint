import unittest

from src.lexing.logic.ts_linter import TsLinter


class TestTsUnusedImports(unittest.TestCase):
    def lint_code(self, code):
        return TsLinter(code).lint()

    def test_used_default_import_is_fine(self):
        code = "import React from 'react';\n\nconsole.log(React);\n"
        self.assertEqual(self.lint_code(code), [])

    def test_unused_default_import_is_reported(self):
        code = "import React from 'react';\n"
        self.assertIn("Line 1: Import 'React' is not used.", self.lint_code(code))

    def test_unused_named_import_is_reported(self):
        code = "import { a, b } from 'lib';\n\nconsole.log(a);\n"
        self.assertEqual(self.lint_code(code), ["Line 1: Import 'b' is not used."])

    def test_alias_is_checked_by_local_name(self):
        code = "import { a as b } from 'lib';\n\nconsole.log(b);\n"
        self.assertEqual(self.lint_code(code), [])

    def test_unused_namespace_import_is_reported(self):
        code = "import * as ns from 'lib';\n"
        self.assertIn("Line 1: Import 'ns' is not used.", self.lint_code(code))

    def test_side_effect_import_is_never_unused(self):
        self.assertEqual(self.lint_code("import './globals.css';\n"), [])

    def test_jsx_component_counts_as_used(self):
        code = "import Header from './Header';\n\nconst a = <Header />;\n"
        self.assertEqual(self.lint_code(code), [])

    def test_type_usage_counts_as_used(self):
        code = "import { Props } from './types';\n\nconst a: Props = {};\n"
        self.assertEqual(self.lint_code(code), [])

    def test_property_access_does_not_count_as_a_use(self):
        code = "import { a } from 'lib';\n\nconsole.log(obj.a);\n"
        self.assertIn("Line 1: Import 'a' is not used.", self.lint_code(code))

    def test_export_counts_as_a_use(self):
        code = "import { a } from 'lib';\n\nexport { a };\n"
        self.assertEqual(self.lint_code(code), [])


if __name__ == '__main__':
    unittest.main()
