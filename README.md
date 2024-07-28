# jay_lint

This is my attempt in making my own linter using [Please](https://github.com/thought-machine/please) from Thought Machine and the python [ast](https://docs.python.org/3/library/ast.html) library

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