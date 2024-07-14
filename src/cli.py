import argparse
import os
import sys
from pathlib import Path

from src.lexing.logic.lexing import JayLinter

def main():
    parser = argparse.ArgumentParser(description='Python Function Comment Linter')
    parser.add_argument('file', type=str, help='Python file to lint')

    args = parser.parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File '{args.file}' not found.")
        return

    if not file_path.is_file() or not file_path.suffix == '.py':
        print(f"Error: '{args.file}' is not a valid Python file.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    linter = JayLinter(source_code)
    messages = linter.lint()

    if messages:
        print("Linting results:")
        for message in messages:
            print(f"- {message}")
    else:
        print("No issues found.")

if __name__ == '__main__':
    main()
