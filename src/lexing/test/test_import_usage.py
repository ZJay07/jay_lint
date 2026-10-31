import unittest

from src.lexing.logic.lexing import JayLinter


class TestImportUsage(unittest.TestCase):
    def lint_code(self, code):
        return JayLinter(source_code=code).lint()

    def fix_code(self, code):
        linter = JayLinter(source_code=code)
        linter.fix()
        return linter.source_code

    def unused_import_messages(self, code):
        return [message for message in self.lint_code(code) if message.startswith("Import ")]

    def test_from_import_used_by_its_bare_name_is_not_reported(self):
        code = "from collections import defaultdict\ncounts = defaultdict(int)\n"
        self.assertEqual(self.unused_import_messages(code), [])

    def test_from_import_that_is_never_used_is_reported(self):
        code = "from collections import defaultdict\ncounts = 1\n"
        self.assertEqual(
            self.unused_import_messages(code),
            ["Import 'collections.defaultdict' on line 1 is not used."],
        )

    def test_import_used_through_its_alias_is_not_reported(self):
        code = "import numpy as np\nvalues = np.zeros(3)\n"
        self.assertEqual(self.unused_import_messages(code), [])

    def test_aliased_import_that_is_never_used_is_reported_by_its_module_name(self):
        code = "import numpy as np\nvalues = 1\n"
        self.assertEqual(
            self.unused_import_messages(code),
            ["Import 'numpy' on line 1 is not used."],
        )

    def test_from_import_used_through_its_alias_is_not_reported(self):
        code = "from collections import defaultdict as dd\ncounts = dd(int)\n"
        self.assertEqual(self.unused_import_messages(code), [])

    def test_dotted_import_used_through_its_top_level_package_is_not_reported(self):
        code = "import os.path\njoined = os.path.join('a', 'b')\n"
        self.assertEqual(self.unused_import_messages(code), [])

    def test_star_import_is_never_reported(self):
        code = "from os import *\nvalue = 1\n"
        self.assertEqual(self.unused_import_messages(code), [])

    def test_future_import_is_never_reported(self):
        code = "from __future__ import annotations\nvalue = 1\n"
        self.assertEqual(self.unused_import_messages(code), [])

    def test_fix_keeps_a_from_import_that_the_code_uses(self):
        code = (
            "from collections import defaultdict\n"
            "\n"
            "\n"
            "def count(words):\n"
            "    counts = defaultdict(int)\n"
            "    return counts\n"
        )
        self.assertIn("from collections import defaultdict", self.fix_code(code))

    def test_fix_still_removes_a_from_import_that_is_unused(self):
        code = "from collections import defaultdict\nvalue = 1\n"
        self.assertNotIn("defaultdict", self.fix_code(code))


if __name__ == "__main__":
    unittest.main()
