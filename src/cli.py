import argparse
import fnmatch
import os
import sys
from pathlib import Path

from src.config import ConfigError, find_config, read_config
from src.lexing.logic.lexing import JayLinter

TS_SUFFIXES = {'.ts', '.tsx', '.mts', '.cts', '.js', '.jsx', '.mjs', '.cjs'}
# These parse without JSX; every other TS/JS suffix uses the TSX grammar.
NON_JSX_SUFFIXES = {'.ts', '.mts', '.cts'}
SKIPPED_DIRECTORIES = {
    'node_modules', '.git', '.next', 'plz-out', 'dist', 'build', '__pycache__', '.venv', 'my_env',
}

def read_source_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_source_file(file_path, source_code):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(source_code)

def print_messages(messages):
    if messages:
        print("Linting results:")
        for message in messages:
            print(f"- {message}")
    else:
        print("No issues found.")

def lint_python(file_path, fix):
    linter = JayLinter(read_source_file(file_path))

    if fix:
        linter.fix()
        write_source_file(file_path, '\n'.join(linter.source_lines))
        print(f"Fixed and saved the file: {file_path}")
        return []

    messages = linter.lint()
    print_messages(messages)
    return messages

def lint_typescript(file_path, fix, max_line_length):
    # tree-sitter needs Python 3.9+, so on older Pythons only the Python linter is available.
    try:
        from src.lexing.logic.ts_linter import TsLinter
    except ImportError:
        print(f"Error: linting '{file_path}' needs Python 3.9 or newer with the "
              "tree-sitter packages: pip install --upgrade jay_lint")
        return ['TypeScript support is not installed']

    # newline='' keeps CRLF files CRLF.
    with open(file_path, 'r', encoding='utf-8', newline='') as f:
        source_code = f.read()
    linter = TsLinter(
        source_code,
        max_line_length=max_line_length,
        tsx=file_path.suffix not in NON_JSX_SUFFIXES,
    )

    if fix:
        fixed = linter.fix()
        if fixed != source_code:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(fixed)
        print(f"Fixed and saved the file: {file_path}")
        return []

    messages = linter.lint()
    print_messages(messages)
    return messages

def collect_files(paths, exclude=(), base='.'):
    """Expand directories into the TypeScript/JavaScript files inside them."""
    files = []
    for path in paths:
        if path.is_dir():
            files.extend(
                sorted(
                    found for found in path.rglob('*')
                    if found.suffix in TS_SUFFIXES
                    and found.is_file()
                    and not SKIPPED_DIRECTORIES.intersection(found.relative_to(path).parts)
                    and not is_excluded(found, exclude, base)
                )
            )
        else:
            files.append(path)
    return files

def is_excluded(file_path, patterns, base):
    """True if any `exclude` pattern matches the file's path or one of its folder names."""
    if not patterns:
        return False
    relative = Path(os.path.relpath(file_path, base))
    candidates = [relative.as_posix(), *relative.parts]
    return any(fnmatch.fnmatch(candidate, pattern)
               for pattern in patterns for candidate in candidates)

def load_settings(config_option):
    """Returns (settings, config_directory), or raises ConfigError."""
    if config_option:
        if not os.path.isfile(config_option):
            raise ConfigError(f"config file '{config_option}' not found.")
        settings = read_config(config_option)
        found = (config_option, settings or {})
    else:
        found = find_config(os.getcwd())
    if found is None:
        return {}, os.getcwd()
    return found[1], os.path.dirname(os.path.abspath(found[0]))

def main(argv=None):
    parser = argparse.ArgumentParser(prog='jlint', description='Python and TypeScript linter')
    parser.add_argument('files', nargs='*', type=str,
                        help='Files or directories to lint (default: "paths" from the config)')
    parser.add_argument('--fix', action='store_true', help="Automatically fix the code")
    parser.add_argument('--max-line-length', type=int, default=None,
                        help='Maximum line length for TypeScript/JavaScript files '
                             '(default: the config value, or 100)')
    parser.add_argument('--strict', action='store_true',
                        help='Exit with status 1 if any issues or errors are found')
    parser.add_argument('--config', type=str, default=None,
                        help='Config file to use (default: jlint.toml or [tool.jlint] in '
                             'pyproject.toml, searched upwards from the current directory)')

    args = parser.parse_args(argv)

    try:
        settings, config_dir = load_settings(args.config)
    except ConfigError as error:
        print(f"Error: {error}")
        return 2

    if args.files:
        paths = [Path(name) for name in args.files]
    else:
        paths = [Path(config_dir) / name for name in settings.get('paths', [])]
    if not paths:
        print("Error: No files given, and no 'paths' in a jlint.toml or [tool.jlint] section.")
        return 2

    max_line_length = args.max_line_length or settings.get('max-line-length', 100)
    strict = args.strict or settings.get('strict', False)
    exclude = settings.get('exclude', [])

    missing = [path for path in paths if not path.exists()]
    for path in missing:
        print(f"Error: File '{path}' not found.")

    files = collect_files([path for path in paths if path.exists()], exclude, config_dir)
    show_headers = len(files) > 1 or any(path.is_dir() for path in paths)
    problems = len(missing)

    for file_path in files:
        if show_headers:
            print(f"\n{file_path}")
        if file_path.suffix == '.py':
            problems += len(lint_python(file_path, args.fix))
        elif file_path.suffix in TS_SUFFIXES:
            problems += len(lint_typescript(file_path, args.fix, max_line_length))
        else:
            print(f"Error: '{file_path}' is not a supported file (.py, .ts, .tsx, .js, .jsx).")
            problems += 1

    return 1 if strict and problems else 0

if __name__ == '__main__':
    sys.exit(main())
