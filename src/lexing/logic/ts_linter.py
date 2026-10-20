from dataclasses import dataclass, field

import tree_sitter_typescript as tst
from tree_sitter import Language, Parser

# Lines touching these nodes are not reported as too long (like ESLint's
# ignoreStrings / ignoreTemplateLiterals / ignoreComments / ignoreRegExpLiterals).
LONG_LINE_EXEMPT_NODES = {'string', 'template_string', 'comment', 'regex'}

# Node's built-in modules, used to group imports (eslint-plugin-import "builtin").
BUILTIN_MODULES = {
    'assert', 'buffer', 'child_process', 'cluster', 'console', 'constants', 'crypto',
    'dgram', 'dns', 'domain', 'events', 'fs', 'http', 'http2', 'https', 'module', 'net',
    'os', 'path', 'perf_hooks', 'process', 'punycode', 'querystring', 'readline', 'repl',
    'stream', 'string_decoder', 'timers', 'tls', 'tty', 'url', 'util', 'v8', 'vm',
    'worker_threads', 'zlib',
}

# Import groups in the order they must appear.
BUILTIN, EXTERNAL, INTERNAL, PARENT, SIBLING, INDEX = range(6)

# Identifier-like nodes that count as a use of an imported name.
USAGE_NODES = {
    'identifier',
    'type_identifier',
    'shorthand_property_identifier',
    'shorthand_property_identifier_pattern',
}

_parsers = {}


def _get_parser(tsx):
    if tsx not in _parsers:
        grammar = tst.language_tsx() if tsx else tst.language_typescript()
        _parsers[tsx] = Parser(Language(grammar))
    return _parsers[tsx]


def import_group(spec):
    if spec.startswith('node:') or spec in BUILTIN_MODULES:
        return BUILTIN
    if spec in ('.', './', './index') or spec.startswith('./index.'):
        return INDEX
    if spec.startswith('../') or spec == '..':
        return PARENT
    if spec.startswith('./'):
        return SIBLING
    if spec.startswith(('@/', '~/', '#')):
        return INTERNAL
    return EXTERNAL


def same_import_group(spec, other):
    return import_group(spec) == import_group(other)


def import_sort_key(spec):
    # eslint-plugin-import alphabetizes segment by segment, ignoring case.
    return (import_group(spec), [part.lower() for part in spec.split('/')])


@dataclass
class ImportInfo:
    node: object
    spec: str
    # (raw text, local name, kind) where kind is 'default', 'named' or 'namespace'.
    bindings: list = field(default_factory=list)

    @property
    def side_effect(self):
        return not self.bindings

    @property
    def line(self):
        return self.node.start_point[0] + 1


class TsLinter:
    def __init__(self, source_code, max_line_length=100, tsx=True):
        self.newline = '\r\n' if '\r\n' in source_code else '\n'
        self.max_line_length = max_line_length
        self.tsx = tsx
        self.messages = []
        self._findings = []
        self._load(source_code.replace('\r\n', '\n'))

    def _load(self, text):
        """(Re)parse `text`, which must use '\\n' line endings."""
        self.source_code = text
        self.source_bytes = text.encode('utf-8')
        self.has_final_newline = text.endswith('\n')
        self.source_lines = text.split('\n')
        if self.has_final_newline:
            self.source_lines.pop()
        self.root = _get_parser(self.tsx).parse(self.source_bytes).root_node
        self.imports = self._collect_imports()

    def _text(self, node):
        return node.text.decode('utf-8')

    def _collect_imports(self):
        imports = []
        for node in self.root.children:
            if node.type != 'import_statement':
                continue
            source = node.child_by_field_name('source')
            info = ImportInfo(node=node, spec=self._text(source)[1:-1])
            clause = next((c for c in node.children if c.type == 'import_clause'), None)
            for part in clause.children if clause else []:
                if part.type == 'identifier':
                    info.bindings.append((self._text(part), self._text(part), 'default'))
                elif part.type == 'namespace_import':
                    name = self._text(next(c for c in part.children if c.type == 'identifier'))
                    info.bindings.append((self._text(part), name, 'namespace'))
                elif part.type == 'named_imports':
                    for spec in (c for c in part.children if c.type == 'import_specifier'):
                        local = spec.child_by_field_name('alias') or spec.child_by_field_name('name')
                        info.bindings.append((self._text(spec), self._text(local), 'named'))
            imports.append(info)
        return imports

    def _walk(self, skip=()):
        """Yield every node depth-first, without descending into `skip` node types."""
        stack = [self.root]
        while stack:
            node = stack.pop()
            yield node
            if node.type not in skip:
                stack.extend(reversed(node.children))

    def _used_names(self):
        return {
            self._text(node)
            for node in self._walk(skip=('import_statement',))
            if node.type in USAGE_NODES
        }

    def _rows_covered_by(self, node_types):
        rows = set()
        for node in self._walk():
            if node.type in node_types:
                rows.update(range(node.start_point[0], node.end_point[0] + 1))
        return rows

    # ---- checks ----

    def _import_runs(self):
        """Runs of imports that are ordered together; side-effect imports split them."""
        runs, current = [], []
        for info in self.imports:
            if info.side_effect:
                if current:
                    runs.append(current)
                current = []
            else:
                current.append(info)
        if current:
            runs.append(current)
        return runs

    def check_import_order(self):
        ordered = [info for run in self._import_runs() for info in run]
        for i, info in enumerate(ordered):
            earlier = next(
                (
                    other for other in ordered[:i]
                    if import_sort_key(other.spec) > import_sort_key(info.spec)
                ),
                None,
            )
            if earlier:
                self._report(
                    info.line,
                    f"'{info.spec}' import should occur before import of '{earlier.spec}'.",
                )
        for previous, info in zip(ordered, ordered[1:]):
            gap = info.node.start_point[0] - previous.node.end_point[0] - 1
            same_group = same_import_group(previous.spec, info.spec)
            if not same_group and gap < 1:
                self._report(info.line, 'There should be a blank line between import groups.')
            elif same_group and gap > 0:
                self._report(info.line, 'There should be no blank line within an import group.')

    def check_unused_imports(self):
        used = self._used_names()
        for info in self.imports:
            for _, name, _ in info.bindings:
                if name not in used:
                    self._report(info.line, f"Import '{name}' is not used.")

    def check_trailing_whitespace(self):
        protected = self._rows_covered_by({'template_string'})
        for row, line in enumerate(self.source_lines):
            if row not in protected and line != line.rstrip():
                self._report(row + 1, 'Line has trailing whitespace.')

    def check_blank_lines(self):
        protected = self._rows_covered_by({'template_string'})
        if self.source_lines and not self.source_lines[0].strip():
            self._report(1, 'The first line is empty.')
        previous_blank = False
        for row, line in enumerate(self.source_lines):
            blank = not line.strip() and row not in protected
            if blank and previous_blank:
                self._report(row + 1, 'Line has more than one consecutive blank line.')
            previous_blank = blank
        if self.source_lines and not self.has_final_newline:
            self._report(len(self.source_lines), 'File should end with a newline.')
        elif len(self.source_lines) > 1 and not self.source_lines[-1].strip():
            self._report(len(self.source_lines), 'File should end with a single newline.')

    def check_line_length(self):
        exempt = self._rows_covered_by(LONG_LINE_EXEMPT_NODES)
        for row, line in enumerate(self.source_lines):
            if len(line) <= self.max_line_length or row in exempt:
                continue
            if 'http://' in line or 'https://' in line:
                continue
            self._report(
                row + 1,
                f'Line exceeds the maximum line length of {self.max_line_length} characters.',
            )

    def _report(self, line, message):
        self._findings.append((line, message))

    def lint(self):
        self._findings = []
        self.check_import_order()
        self.check_unused_imports()
        self.check_trailing_whitespace()
        self.check_blank_lines()
        self.check_line_length()
        self._findings.sort(key=lambda finding: finding[0])
        self.messages = [f'Line {line}: {message}' for line, message in self._findings]
        return self.messages

    # ---- fixes ----

    def _apply_edits(self, edits):
        """Apply (start_byte, end_byte, replacement) edits, then reparse."""
        data = self.source_bytes
        for start, end, replacement in sorted(edits, reverse=True):
            data = data[:start] + replacement.encode('utf-8') + data[end:]
        self._load(data.decode('utf-8'))

    def _rebuild_import(self, info, used):
        """New text for an import with its unused bindings dropped, or None if unchanged."""
        kept = [binding for binding in info.bindings if binding[1] in used]
        if len(kept) == len(info.bindings):
            return None
        if not kept:
            return ''
        node = info.node
        parts = [raw for raw, _, kind in kept if kind != 'named']
        named = [raw for raw, _, kind in kept if kind == 'named']
        if named:
            parts.append('{ ' + ', '.join(named) + ' }')
        type_prefix = 'type ' if node.children[1].type == 'type' else ''
        quote = self._text(node.child_by_field_name('source'))[0]
        semicolon = ';' if node.children[-1].type == ';' else ''
        return f"import {type_prefix}{', '.join(parts)} from {quote}{info.spec}{quote}{semicolon}"

    def fix_unused_imports(self):
        used = self._used_names()
        edits = []
        for info in self.imports:
            replacement = self._rebuild_import(info, used)
            if replacement is None:
                continue
            start, end = info.node.start_byte, info.node.end_byte
            if replacement == '' and self.source_bytes[end:end + 1] == b'\n':
                end += 1
            edits.append((start, end, replacement))
        if edits:
            self._apply_edits(edits)

    def _can_sort(self, run):
        """A run is only sorted when nothing but imports lies between its first and last."""
        start, end = run[0].node.start_byte, run[-1].node.end_byte
        members = {info.node.start_byte for info in run}
        return not any(
            start <= child.start_byte <= end and child.start_byte not in members
            for child in self.root.children
        )

    def fix_import_order(self):
        edits = []
        for run in self._import_runs():
            if len(run) < 2 or not self._can_sort(run):
                continue
            ordered = sorted(run, key=lambda info: import_sort_key(info.spec))
            blocks = []
            for i, info in enumerate(ordered):
                if i:
                    same_group = same_import_group(ordered[i - 1].spec, info.spec)
                    blocks.append('\n' if same_group else '\n\n')
                blocks.append(self._text(info.node))
            start, end = run[0].node.start_byte, run[-1].node.end_byte
            new_text = ''.join(blocks)
            if new_text.encode('utf-8') != self.source_bytes[start:end]:
                edits.append((start, end, new_text))
        if edits:
            self._apply_edits(edits)

    def fix_whitespace(self):
        protected = self._rows_covered_by({'template_string'})
        lines, previous_blank = [], True  # starting True drops leading blank lines
        for row, line in enumerate(self.source_lines):
            if row in protected:
                lines.append(line)
                previous_blank = False
                continue
            line = line.rstrip()
            blank = not line
            if blank and previous_blank:
                continue
            lines.append(line)
            previous_blank = blank
        while lines and not lines[-1]:
            lines.pop()
        self._load('\n'.join(lines) + '\n' if lines else '')

    def fix(self):
        """Fix what can be fixed and return the new source text."""
        self.fix_unused_imports()
        self.fix_import_order()
        self.fix_whitespace()
        self.source_code = self.source_code.replace('\n', self.newline)
        return self.source_code
