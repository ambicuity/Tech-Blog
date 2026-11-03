"""Show what the default encoding does, under both UTF-8 modes.

Pinned versions: Python 3.12.3 measured in this run; Python 3.15 is the
target, where PEP 686 makes UTF-8 mode the default. No Python 3.15
interpreter is available in this environment, so this module does NOT
claim to run on 3.15. It runs the two modes that 3.15 switches between
on an older interpreter: UTF-8 mode off (the pre-3.15 default under a
non-UTF-8 locale) and UTF-8 mode on (the 3.15 default). The child
process is the only place a bare ``open()`` appears, and it appears
inside a string, so the scanner in ``find_implicit.py`` does not flag
this file: the bare call is the behaviour under test, not code to ship.

Run it:

    python3 modes.py

It writes two small files to a temporary directory (one UTF-8, one
cp1252), reads each one under both modes, and prints the outcome.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# The child script is a string on purpose: it must call open() with no
# encoding argument, because that call is the thing being measured.
CHILD = (
    "import json, locale, sys\n"
    "path = sys.argv[1]\n"
    "try:\n"
    "    text = open(path).read()\n"
    "    result = {'text': text, 'error': None}\n"
    "except UnicodeDecodeError as exc:\n"
    "    result = {'text': None, 'error': type(exc).__name__}\n"
    "result['preferred'] = locale.getpreferredencoding(False)\n"
    "result['utf8_mode'] = bool(sys.flags.utf8_mode)\n"
    "print(json.dumps(result))\n"
)


def read_under_mode(path, utf8_mode):
    """Read ``path`` with a bare open() under one UTF-8 mode.

    ``utf8_mode`` True means ``-X utf8=1`` (the Python 3.15 default);
    False means ``-X utf8=0`` with a C locale and locale coercion
    disabled (the pre-3.15 behaviour under a non-UTF-8 locale).
    Returns a dict with ``preferred``, ``utf8_mode``, ``text`` and
    ``error`` (the error class name, or None).
    """
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env["PYTHONCOERCECLOCALE"] = "0"
    env.pop("PYTHONUTF8", None)
    env.pop("PYTHONIOENCODING", None)
    flag = "utf8=1" if utf8_mode else "utf8=0"
    proc = subprocess.run(
        [sys.executable, "-X", flag, "-c", CHILD, str(path)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(proc.stdout.strip().splitlines()[-1])


def read_explicit(path, encoding):
    """Read ``path`` with an explicit encoding, in this process."""
    return Path(path).read_text(encoding=encoding)


def demo():
    """Run both modes over both fixtures; return the raw results."""
    with tempfile.TemporaryDirectory(prefix="utf8-default-") as tmp:
        root = Path(tmp)
        utf8_file = root / "utf8.txt"
        legacy_file = root / "legacy.txt"
        utf8_file.write_bytes("café\n".encode("utf-8"))
        legacy_file.write_bytes("café\n".encode("cp1252"))
        results = {}
        for label, mode in (("old", False), ("new", True)):
            results[label] = {
                "utf8_bytes": read_under_mode(utf8_file, mode),
                "legacy_bytes": read_under_mode(legacy_file, mode),
            }
        results["explicit_utf8_under_old"] = read_under_mode_explicit(
            utf8_file, "utf-8", False
        )
        results["explicit_cp1252_under_new"] = read_under_mode_explicit(
            legacy_file, "cp1252", True
        )
        for label, mode in (("old", False), ("new", True)):
            outcome = results[label]["utf8_bytes"]
            print(
                f"{label} mode: preferred={outcome['preferred']} "
                f"utf8_mode={outcome['utf8_mode']} "
                f"utf8_bytes -> {outcome['text']!r} "
                f"error={outcome['error']}"
            )
            legacy = results[label]["legacy_bytes"]
            print(
                f"{label} mode: legacy_bytes -> {legacy['text']!r} "
                f"error={legacy['error']}"
            )
        print(
            "explicit utf-8 under old mode:",
            results["explicit_utf8_under_old"],
        )
        print(
            "explicit cp1252 under new mode:",
            results["explicit_cp1252_under_new"],
        )
        return results


def read_under_mode_explicit(path, encoding, utf8_mode):
    """Read ``path`` with an explicit encoding under one UTF-8 mode."""
    child = (
        "import json, sys\n"
        "print(json.dumps({'text': open(sys.argv[1], "
        "encoding=sys.argv[2]).read()}))\n"
    )
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env["PYTHONCOERCECLOCALE"] = "0"
    env.pop("PYTHONUTF8", None)
    flag = "utf8=1" if utf8_mode else "utf8=0"
    proc = subprocess.run(
        [sys.executable, "-X", flag, "-c", child, str(path), encoding],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(proc.stdout.strip().splitlines()[-1])["text"]


if __name__ == "__main__":
    demo()
