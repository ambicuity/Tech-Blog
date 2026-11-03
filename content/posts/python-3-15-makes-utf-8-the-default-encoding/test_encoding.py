"""Tests for modes.py and find_implicit.py.

Run from the article folder:

    python3 -W error::DeprecationWarning -m unittest test_encoding -v

Measured on Python 3.12.3. The mode tests toggle UTF-8 mode with
``-X utf8=``: mode off under a C locale is the pre-3.15 default, mode
on is the Python 3.15 default per PEP 686. Nothing here claims to
have run on a Python 3.15 interpreter.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from find_implicit import collect, scan_file  # noqa: E402
from modes import demo, read_explicit, read_under_mode  # noqa: E402


def write_fixture(directory, name, source):
    path = Path(directory) / name
    path.write_text(source, encoding="utf-8")
    return path


class ModeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="test-utf8-")
        self.root = Path(self.tmp.name)
        self.utf8_file = self.root / "utf8.txt"
        self.legacy_file = self.root / "legacy.txt"
        self.utf8_file.write_bytes("café\n".encode("utf-8"))
        self.legacy_file.write_bytes("café\n".encode("cp1252"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_old_mode_preferred_encoding_is_ascii(self):
        result = read_under_mode(self.utf8_file, False)
        self.assertEqual(result["preferred"], "ANSI_X3.4-1968")
        self.assertFalse(result["utf8_mode"])

    def test_new_mode_preferred_encoding_is_utf8(self):
        result = read_under_mode(self.utf8_file, True)
        # Case differs by platform and mode (utf-8 vs UTF-8); compare folded.
        self.assertEqual(result["preferred"].lower(), "utf-8")
        self.assertTrue(result["utf8_mode"])

    def test_old_mode_raises_on_utf8_bytes(self):
        result = read_under_mode(self.utf8_file, False)
        self.assertIsNone(result["text"])
        self.assertEqual(result["error"], "UnicodeDecodeError")

    def test_new_mode_reads_utf8_bytes(self):
        result = read_under_mode(self.utf8_file, True)
        self.assertEqual(result["text"], "café\n")
        self.assertIsNone(result["error"])

    def test_new_mode_raises_on_legacy_bytes(self):
        result = read_under_mode(self.legacy_file, True)
        self.assertIsNone(result["text"])
        self.assertEqual(result["error"], "UnicodeDecodeError")

    def test_explicit_utf8_reads_under_old_mode(self):
        self.assertEqual(read_explicit(self.utf8_file, "utf-8"), "café\n")

    def test_explicit_cp1252_reads_legacy_bytes(self):
        self.assertEqual(read_explicit(self.legacy_file, "cp1252"), "café\n")

    def test_demo_reports_both_modes(self):
        results = demo()
        self.assertEqual(results["old"]["utf8_bytes"]["error"], "UnicodeDecodeError")
        self.assertEqual(results["new"]["utf8_bytes"]["text"], "café\n")
        self.assertEqual(results["explicit_utf8_under_old"], "café\n")
        self.assertEqual(results["explicit_cp1252_under_new"], "café\n")


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="test-scan-")
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_finds_bare_open(self):
        path = write_fixture(self.root, "a.py", "with open('x.txt') as f:\n    f.read()\n")
        findings = scan_file(path)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "implicit-encoding")

    def test_ignores_explicit_encoding(self):
        path = write_fixture(
            self.root, "a.py", "with open('x.txt', encoding='utf-8') as f:\n    f.read()\n"
        )
        self.assertEqual(scan_file(path), [])

    def test_ignores_binary_mode(self):
        path = write_fixture(self.root, "a.py", "with open('x.bin', 'rb') as f:\n    f.read()\n")
        self.assertEqual(scan_file(path), [])

    def test_ignores_explicit_locale_encoding(self):
        path = write_fixture(
            self.root, "a.py", "with open('x.txt', encoding='locale') as f:\n    f.read()\n"
        )
        self.assertEqual(scan_file(path), [])

    def test_finds_path_read_text_without_encoding(self):
        path = write_fixture(self.root, "a.py", "from pathlib import Path\nPath('x.txt').read_text()\n")
        findings = scan_file(path)
        self.assertEqual(len(findings), 1)
        self.assertIn("read_text", findings[0].message)

    def test_ignores_path_read_text_with_encoding(self):
        path = write_fixture(
            self.root, "a.py", "from pathlib import Path\nPath('x.txt').read_text(encoding='utf-8')\n"
        )
        self.assertEqual(scan_file(path), [])

    def test_finds_path_open_without_encoding(self):
        path = write_fixture(self.root, "a.py", "from pathlib import Path\nPath('x.txt').open()\n")
        self.assertEqual(len(findings := scan_file(path)), 1)
        self.assertEqual(findings[0].kind, "implicit-encoding")

    def test_dynamic_mode_is_not_flagged(self):
        # Documented limitation: a variable mode cannot be proven text.
        path = write_fixture(self.root, "a.py", "mode = get_mode()\nwith open('x.txt', mode) as f:\n    f.read()\n")
        self.assertEqual(scan_file(path), [])

    def test_flags_getpreferredencoding(self):
        path = write_fixture(self.root, "a.py", "import locale\nlocale.getpreferredencoding(False)\n")
        findings = scan_file(path)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "preferred-encoding")

    def test_unparseable_file_is_skipped(self):
        path = write_fixture(self.root, "a.py", "def broken(:\n")
        self.assertEqual(scan_file(path), [])

    def test_cli_exits_1_on_findings_and_0_when_clean(self):
        dirty = write_fixture(self.root, "dirty.py", "open('x.txt')\n")
        clean = write_fixture(self.root, "clean.py", "open('x.txt', encoding='utf-8')\n")
        scanner = str(Path(__file__).resolve().parent / "find_implicit.py")
        dirty_run = subprocess.run(
            [sys.executable, scanner, str(dirty)],
            capture_output=True, text=True, encoding="utf-8",
        )
        clean_run = subprocess.run(
            [sys.executable, scanner, str(clean)],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(dirty_run.returncode, 1)
        self.assertIn("implicit-encoding", dirty_run.stdout)
        self.assertEqual(clean_run.returncode, 0)

    def test_collect_walks_a_directory(self):
        write_fixture(self.root, "a.py", "open('x.txt')\n")
        write_fixture(self.root, "b.py", "open('x.txt', encoding='utf-8')\n")
        self.assertEqual(len(collect([str(self.root)])), 1)


if __name__ == "__main__":
    unittest.main()
