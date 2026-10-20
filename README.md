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
After installing, simply run `jays-linter` followed by your file name.
eg:
```bash
jays-linter <test.py>
```

# How to use 'fix'?
Same as before, just add `--fix` after the file name
eg:
```bash
jays-linter --fix <test.py>
```

# Development (Please)
Tests run under Please, pinned to the Python in `.python-version` (currently 3.11) so local and CI match.
Please builds with its own restricted `PATH`, so it ignores the `python3` on yours; `scripts/use_uv_python.sh` installs the pinned Python with [uv](https://docs.astral.sh/uv/) and points Please at it (via an untracked `.plzconfig.local`).
```bash
./scripts/use_uv_python.sh
./pleasew test //src/...
```
