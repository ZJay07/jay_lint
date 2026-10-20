# jay_lint
[![Build and Test](https://github.com/ZJay07/jay_lint/actions/workflows/unittest_feature.yml/badge.svg)](https://github.com/ZJay07/jay_lint/actions/workflows/unittest_feature.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is my attempt in making my own linter using [Please](https://github.com/thought-machine/please) from Thought Machine and the python [ast](https://docs.python.org/3/library/ast.html) library

# Install it via pip
```bash
pip install jay_lint
```

# To install, on the root directory run:
```bash
pip install .
```

# How to use?
After installing, simply run `jlint` followed by your file name.
eg:
```bash
jlint <test.py>
```

# How to use 'fix'?
Same as before, just add `--fix` after the file name
eg:
```bash
jlint --fix <test.py>
```

# TypeScript / JavaScript support
`jlint` also lints `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs` files. It parses them with
[tree-sitter](https://tree-sitter.github.io/) (installed with the package; needs Python 3.9+):
```bash
jlint app/page.tsx                      # one file
jlint app components lib                # directories (node_modules, .next, plz-out skipped)
jlint --fix components/Bio.tsx          # fix in place
jlint --strict --max-line-length 88 app # exit 1 if anything is reported (for CI)
```

Checks (`--fix` can fix the ones marked *fix*):

| Check | |
| --- | --- |
| Import order and blank lines between import groups (builtin, external, `@/` internal, parent, sibling, index; alphabetised) | *fix* |
| Unused imports (default, named, aliased, namespace; side-effect imports are never unused) | *fix* |
| Trailing whitespace, repeated or leading blank lines, final newline | *fix* |
| Line length (`--max-line-length`, default 100). Lines containing a string, template literal, comment, regex or URL are not reported | |

The import order rules mirror `eslint-plugin-import`'s `import/order` with
`alphabetize` and `newlines-between: always`, so the two agree. Imports are only reordered
when nothing but imports sits between them; a comment between two imports leaves them alone.

# Development (Please)
Tests run under Please, pinned to the Python in `.python-version` (currently 3.11) so local and CI match.
Please builds with its own restricted `PATH`, so it ignores the `python3` on yours; `scripts/use_uv_python.sh` installs the pinned Python with [uv](https://docs.astral.sh/uv/) and points Please at it (via an untracked `.plzconfig.local`).
```bash
./scripts/use_uv_python.sh
./pleasew test //src/...
```
