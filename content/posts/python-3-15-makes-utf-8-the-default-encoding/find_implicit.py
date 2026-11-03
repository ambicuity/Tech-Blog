"""Find text-file calls that rely on the default encoding.

Usage:

    python3 find_implicit.py path/to/file.py path/to/package/

Exit status 1 when any finding is reported, 0 when the scanned code
is clean. Directories are walked for ``.py`` files; ``__pycache__``
directories are skipped.

What it flags, per file, with file and line:

* ``open(...)``, ``io.open(...)`` and ``Path.open(...)`` in text mode
  with no ``encoding`` keyword. Binary mode (``"rb"``, ``"wb"`` and
  friends) is not flagged: the default encoding does not apply to it.
* ``Path.read_text(...)`` and ``Path.write_text(...)`` with no
  ``encoding`` keyword. Both default to the platform encoding, so
  both move when the default moves.
* ``locale.getpreferredencoding(...)`` calls. That function follows
  UTF-8 mode, so it reports UTF-8 on Python 3.15 even when the locale
  is not UTF-8; code that needs the real locale encoding should use
  ``locale.getencoding()`` instead (added in Python 3.11).

What it deliberately does NOT flag (documented limitations, not bugs
to fix by widening the scan silently):

* A call whose mode is a variable, not a literal string. The scanner
  cannot tell whether such a call is binary, so it stays silent
  rather than crying wolf.
* ``io.TextIOWrapper`` constructed without ``encoding``, and
  ``subprocess`` text mode. Those need data-flow analysis, not an
  AST walk; find them with ``-X warn_default_encoding`` (see the
  article) and review the hits by hand.
* A file that does not parse. The scanner prints a warning to
  stderr and skips it, so one broken file cannot hide the rest.

Every ``encoding`` value is accepted, including ``encoding="locale"``:
the point is that the choice is explicit, not that it is UTF-8.
"""

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

TEXT_OPEN_NAMES = {"open"}
PATH_TEXT_METHODS = {"read_text", "write_text"}


@dataclass
class Finding:
    path: str
    line: int
    kind: str
    message: str

    def __str__(self):
        return f"{self.path}:{self.line}: {self.kind}: {self.message}"


def _has_encoding(keywords):
    return any(kw.arg == "encoding" for kw in keywords)


def _mode_is_binary(node):
    """True when the mode argument is a literal containing 'b'."""
    mode = None
    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
        mode = node.args[1].value
    for kw in node.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            mode = kw.value.value
    return isinstance(mode, str) and "b" in mode


def _mode_is_dynamic(node):
    """True when a mode argument exists but is not a string literal."""
    if len(node.args) >= 2 and not isinstance(node.args[1], ast.Constant):
        return True
    return any(
        kw.arg == "mode" and not isinstance(kw.value, ast.Constant)
        for kw in node.keywords
    )


def _is_open_call(node):
    if isinstance(node.func, ast.Name):
        return node.func.id in TEXT_OPEN_NAMES
    if isinstance(node.func, ast.Attribute):
        return node.func.attr == "open"
    return False


def _is_path_text_call(node):
    return (
        isinstance(node.func, ast.Attribute)
        and node.func.attr in PATH_TEXT_METHODS
    )


def _is_preferred_encoding_call(node):
    return (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "getpreferredencoding"
    )


class _Visitor(ast.NodeVisitor):
    def __init__(self, path):
        self.path = path
        self.findings = []

    def visit_Call(self, node):
        if _is_open_call(node):
            if (
                not _has_encoding(node.keywords)
                and not _mode_is_binary(node)
                and not _mode_is_dynamic(node)
            ):
                self.findings.append(
                    Finding(
                        self.path,
                        node.lineno,
                        "implicit-encoding",
                        "open() without encoding= relies on the default encoding",
                    )
                )
        elif _is_path_text_call(node):
            if not _has_encoding(node.keywords):
                self.findings.append(
                    Finding(
                        self.path,
                        node.lineno,
                        "implicit-encoding",
                        f"Path.{node.func.attr}() without encoding= "
                        "relies on the default encoding",
                    )
                )
        elif _is_preferred_encoding_call(node):
            self.findings.append(
                Finding(
                    self.path,
                    node.lineno,
                    "preferred-encoding",
                    "locale.getpreferredencoding() follows UTF-8 mode; "
                    "use locale.getencoding() for the real locale encoding",
                )
            )
        self.generic_visit(node)


def scan_file(path):
    """Return the findings for one file; [] for an unparseable file."""
    source = Path(path).read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        print(f"warning: skipping unparseable file {path}: {exc}", file=sys.stderr)
        return []
    visitor = _Visitor(str(path))
    visitor.visit(tree)
    return visitor.findings


def collect(paths):
    """Return findings for every .py file under ``paths``."""
    findings = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files = sorted(p for p in path.rglob("*.py") if "__pycache__" not in p.parts)
        elif path.suffix == ".py":
            files = [path]
        else:
            continue
        for file_path in files:
            findings.extend(scan_file(file_path))
    return findings


def main(argv):
    if len(argv) < 2:
        print("usage: python3 find_implicit.py <path> [<path> ...]", file=sys.stderr)
        return 2
    findings = collect(argv[1:])
    for finding in findings:
        print(finding)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
