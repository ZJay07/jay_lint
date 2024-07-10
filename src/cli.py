import argparse
import ast
import os
import sys
from src.lexing.logic.lexing import FunctionArgLinter

green_start = "\033[92m"

def parse_arguments():
    parser = argparse.ArgumentParser(description='A custom Python linter')
    parser.add_argument('filepath', type=str, help='Path to the Python file to lint')
    parser.add_argument('--max-args', type=int, default=4, help='Maximum allowed number of arguments in functions')
    parser.add_argument('--max-line-length', type=int, default=79, help='Maximum allowed line length')
    return parser.parse_args()

def main():
    args = parse_arguments()
    filepath = args.filepath

    if not os.path.isfile(filepath):
        print(f"Error: File '{filepath}' not found.")
        return

    with open(filepath, 'r') as file:
        source_code = file.read()

    source_lines = source_code.splitlines()
    linter = FunctionArgLinter(max_args=args.max_args, source_lines=source_lines, max_line_length=args.max_line_length)
    tree = ast.parse(source_code)
    linter.visit(tree)
    linter.check_line_length()
    linter.finalize()

    if linter.messages:
        for message in linter.messages:
            print(message)
    else:
        print(f"{green_start}No issues found in '{filepath}'.")

if __name__ == '__main__':
    main()
