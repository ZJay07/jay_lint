import argparse
from pathlib import Path

from src.lexing.logic.lexing import JayLinter

def read_source_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_source_file(file_path, source_code):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(source_code)

def main():
    parser = argparse.ArgumentParser(description='Python Function Comment Linter')
    parser.add_argument('file', type=str, help='Python file to lint')
    parser.add_argument('--fix', action='store_true', help="Automatically fix the code")

    args = parser.parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File '{args.file}' not found.")
        return

    if not file_path.is_file() or not file_path.suffix == '.py':
        print(f"Error: '{args.file}' is not a valid Python file.")
        return

    source_code = read_source_file(file_path)

    linter = JayLinter(source_code)

    if args.fix:
        linter.fix()
        write_source_file(file_path, '\n'.join(linter.source_lines))
        print(f"Fixed and saved the file: {args.file}")
    else:
        messages = linter.lint()
        if messages:
            print("Linting results:")
            for message in messages:
                print(f"- {message}")
        else:
            print("No issues found.")

if __name__ == '__main__':
    main()
