#!/usr/bin/env python3
"""duckcheck: pre-upgrade checks for the DuckDB 1.x to 2.0 move.

Runs the semantics probes that distinguish DuckDB 1.x from 2.0, verifies
the compatibility bridges, and checks whether a database file written by
one version can be opened by the other.

Usage:
    python3 duckcheck.py [--old-python PATH] [dbfile]

With no dbfile, a scratch file with three rows is created and checked.
--old-python points at a Python interpreter with duckdb 1.x installed;
without it, only the current interpreter's checks run.

Requires duckdb 1.5.x or 2.0.x and Python 3.11+. No Arrow calls: on some
builds the 2.0.0 Arrow output path is unusable, and this tool never needs it.
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import duckdb

# Expected probe outcomes per major line. "1.x" is the old behavior,
# "2.0" is the new behavior. Anything else is reported as unknown.
EXPECTED = {
    "regex_partial": {"1.x": False, "2.0": True},
    "factorial": {"1.x": 720, "2.0": 12},
    "int_div_zero": {"1.x": None, "2.0": "InvalidInputException"},
    "mod_zero": {"1.x": None, "2.0": "InvalidInputException"},
    "float_div_zero": {"1.x": float("inf"), "2.0": float("inf")},
    "hex_literal_type": {"1.x": "VARCHAR", "2.0": "BLOB"},
    "bit_literal_type": {"1.x": "VARCHAR", "2.0": "BIT"},
    "lambda_single_arrow": {"1.x": [2, 3, 4], "2.0": "BinderException"},
    "ctas_null_type": {"1.x": "INTEGER", "2.0": '"NULL"'},
    "tx_after_failed_select": {"1.x": "insert committed",
                               "2.0": "TransactionException"},
    # 2.0.1 restored the 1.x behavior: a double-matched MERGE completes
    # silently. 2.0.0 is the odd version out (it raises
    # InvalidInputException); test_duckcheck.py covers that split by exact
    # version, since this map only distinguishes the 1.x and 2.0 lines.
    "merge_double_match": {"1.x": "merged silently",
                           "2.0": "merged silently"},
}

PROBE_SQL = {
    "regex_partial": "SELECT 'abc' ~ 'b'",
    "factorial": "SELECT 2 * 3!",
    "int_div_zero": "SELECT 1 // 0",
    "mod_zero": "SELECT 1 % 0",
    "float_div_zero": "SELECT 1 / 0",
    "hex_literal_type": "SELECT typeof(X'6162')",
    "bit_literal_type": "SELECT typeof(B'1010')",
    "lambda_single_arrow": "SELECT list_transform([1, 2, 3], x -> x + 1)",
}


def major(version):
    """'2.0.0' -> '2.0', '1.5.6' -> '1.x'."""
    return "2.0" if version.startswith("2.") else "1.x"


def run_sql(con, sql):
    """Run one statement; return the value or 'ErrorType' on failure."""
    try:
        return con.execute(sql).fetchone()[0]
    except Exception as exc:  # noqa: BLE001 - probe output by design
        return type(exc).__name__


def semantics_probes(con):
    """Run every behavior probe; return {name: observed}."""
    out = {}
    for name, sql in PROBE_SQL.items():
        out[name] = run_sql(con, sql)
    con.execute("CREATE TABLE probe_null AS SELECT NULL AS x")
    out["ctas_null_type"] = con.execute(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name = 'probe_null'").fetchone()[0]
    con.execute("CREATE TABLE probe_tx (x INTEGER)")
    con.execute("BEGIN")
    try:
        con.execute("SELECT * FROM probe_missing_table")
    except Exception:  # noqa: BLE001 - the failure is the probe
        pass
    try:
        con.execute("INSERT INTO probe_tx VALUES (1)")
        con.execute("COMMIT")
        out["tx_after_failed_select"] = "insert committed"
    except Exception as exc:  # noqa: BLE001 - the failure is the probe
        try:
            con.execute("ROLLBACK")
        except Exception:  # noqa: BLE001 - best effort cleanup
            pass
        out["tx_after_failed_select"] = type(exc).__name__
    con.execute("CREATE TABLE probe_m_t (id INTEGER PRIMARY KEY, v INTEGER)")
    con.execute("INSERT INTO probe_m_t VALUES (1, 10)")
    con.execute("CREATE TABLE probe_m_s (id INTEGER, v INTEGER)")
    con.execute("INSERT INTO probe_m_s VALUES (1, 20), (1, 30)")
    try:
        con.execute("MERGE INTO probe_m_t USING probe_m_s "
                    "ON probe_m_t.id = probe_m_s.id "
                    "WHEN MATCHED THEN UPDATE SET v = probe_m_s.v")
        out["merge_double_match"] = "merged silently"
    except Exception as exc:  # noqa: BLE001 - the failure is the probe
        out["merge_double_match"] = type(exc).__name__
    return out


def check_bridges(con):
    """Verify each 2.0 compatibility bridge restores the 1.x behavior.

    Returns {bridge: True/False}. Only meaningful on DuckDB 2.0.
    """
    out = {}
    con.execute("SET regex_match_operator_semantics = 'full'")
    out["regex_full"] = run_sql(con, "SELECT 'abc' ~ 'b'") is False
    con.execute("SET regex_match_operator_semantics = 'partial'")
    con.execute("SET lambda_syntax = 'enable_single_arrow'")
    out["lambda_bridge"] = run_sql(
        con, "SELECT list_transform([1, 2, 3], x -> x + 1)") == [2, 3, 4]
    con.execute("SET error_on_division_by_zero = false")
    out["div_zero_bridge"] = run_sql(con, "SELECT 1 // 0") is None
    con.execute("SET error_on_division_by_zero = true")
    out["try_div_zero"] = run_sql(con, "SELECT TRY(1 // 0)") is None
    con.execute("SET legacy_disable_null_type = true")
    con.execute("CREATE TABLE probe_null_bridge AS SELECT NULL AS x")
    out["null_type_bridge"] = con.execute(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name = 'probe_null_bridge'").fetchone()[0] == "INTEGER"
    con.execute(
        "SET default_transaction_invalidation_policy = "
        "'SYNTACTIC_ERRORS_DO_NOT_INVALIDATE'")
    con.execute("CREATE TABLE probe_tx_bridge (x INTEGER)")
    con.execute("BEGIN")
    try:
        con.execute("SELECT * FROM probe_missing_table")
    except Exception:  # noqa: BLE001 - the failure is the probe
        pass
    try:
        con.execute("INSERT INTO probe_tx_bridge VALUES (1)")
        con.execute("COMMIT")
        out["tx_bridge"] = True
    except Exception:  # noqa: BLE001 - the failure is the probe
        try:
            con.execute("ROLLBACK")
        except Exception:  # noqa: BLE001 - best effort cleanup
            pass
        out["tx_bridge"] = False
    return out


def run_with(python, code):
    """Run a snippet under another interpreter; return (ok, stdout, stderr)."""
    proc = subprocess.run([python, "-c", code], capture_output=True,
                          text=True, timeout=120)
    return proc.returncode == 0, proc.stdout.strip(), proc.stderr.strip()[-2000:]


OPEN_CODE = (
    "import duckdb, sys;"
    "c = duckdb.connect(sys.argv[1], read_only=True);"
    "print(c.execute('SELECT count(*), sum(amount) FROM t').fetchone())"
)

VERSION_CODE = "import duckdb; print(duckdb.__version__)"


def check_file(python, path):
    """Can this interpreter open the file? Return (ok, detail).

    The detail is the most informative line of the failure: the first
    line that names the error, so a storage-version rejection reads
    as the version mismatch rather than the help footer.
    """
    code = OPEN_CODE
    ok, out, err = run_with(python, code.replace(
        "sys.argv[1]", repr(str(path))))
    if ok:
        return True, out
    lines = [line for line in err.splitlines() if line.strip()]
    for line in lines:
        if "Error" in line:
            # Tracebacks print "module.ExceptionType: message"; report
            # the message, which names the failure.
            match = re.match(r"^[\w.]+(?:Error|Exception|Warning): (.*)$",
                             line)
            if match and "Error" in match.group(1):
                return False, match.group(1)
            return False, line
    return False, lines[0] if lines else "open failed"


def create_demo_file(path, python):
    """Create a three-row file with the given interpreter, default storage."""
    code = (
        "import duckdb, sys;"
        "c = duckdb.connect(sys.argv[1]);"
        "c.execute('CREATE TABLE t (id INTEGER, amount DECIMAL(10, 2))');"
        "c.execute(\"INSERT INTO t VALUES (1, 10.50), (2, 7.25), (3, 11.00)\");"
        "c.close()"
    )
    ok, _, err = run_with(python, code.replace("sys.argv[1]", repr(str(path))))
    if not ok:
        raise RuntimeError(f"could not create demo file: {err}")


def create_compat_file(path, python):
    """Create a file with storage_compatibility_version='v1.5.6'."""
    code = (
        "import duckdb, sys;"
        "c = duckdb.connect(sys.argv[1],"
        " config={'storage_compatibility_version': 'v1.5.6'});"
        "c.execute('CREATE TABLE t (id INTEGER, amount DECIMAL(10, 2))');"
        "c.execute(\"INSERT INTO t VALUES (1, 10.50), (2, 7.25), (3, 11.00)\");"
        "c.close()"
    )
    ok, _, err = run_with(python, code.replace("sys.argv[1]", repr(str(path))))
    if not ok:
        raise RuntimeError(f"could not create compat file: {err}")


def report(dbfile, old_python):
    """Build the upgrade report as a dict."""
    version = duckdb.__version__
    line = major(version)
    con = duckdb.connect()
    probes = semantics_probes(con)
    verdicts = {name: ("2.0" if probes[name] == EXPECTED[name]["2.0"]
                       else "1.x" if probes[name] == EXPECTED[name]["1.x"]
                       else "unknown")
                for name in EXPECTED}
    result = {
        "engine": version,
        "line": line,
        "probes": probes,
        "verdicts": verdicts,
        "bridges": check_bridges(con) if line == "2.0" else {},
        "files": {},
    }
    con.close()
    if old_python:
        ok, out, _ = run_with(old_python, VERSION_CODE)
        result["old_engine"] = out if ok else "unknown"
        if dbfile is not None:
            new_ok, new_detail = check_file(sys.executable, dbfile)
            old_ok, old_detail = check_file(old_python, dbfile)
            result["files"][str(dbfile)] = {
                "new_opens": new_ok, "new_detail": new_detail,
                "old_opens": old_ok, "old_detail": old_detail,
            }
    return result


def print_report(result):
    print(f"engine: duckdb {result['engine']} ({result['line']} line)")
    if "old_engine" in result:
        print(f"old interpreter: duckdb {result['old_engine']}")
    print("\nsemantics probes (observed -> behavior):")
    for name, observed in result["probes"].items():
        print(f"  {name}: {observed!r} -> {result['verdicts'][name]}")
    if result["bridges"]:
        print("\ncompatibility bridges (True = 1.x behavior restored):")
        for name, ok in result["bridges"].items():
            print(f"  {name}: {ok}")
    for path, check in result["files"].items():
        print(f"\nfile: {path}")
        print(f"  new engine opens it: {check['new_opens']} ({check['new_detail']})")
        print(f"  old engine opens it: {check['old_opens']} ({check['old_detail']})")
    if result["files"]:
        any_blocked = any(not c["old_opens"]
                          for c in result["files"].values())
        print("\nrecommendation: " + (
            "this file is already on the one-way side: keep a pre-upgrade "
            "copy and write new files with an explicit storage version "
            "while any 1.x process remains."
            if any_blocked else
            "this file is still readable by the old version: it has not "
            "crossed the storage-format door yet."))
    print("\nrecommendation: run a shadow system on 2.0.1, diff the results "
          "of your real queries, and only then roll the fleet forward.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Pre-upgrade checks for the DuckDB 1.x to 2.0 move.")
    parser.add_argument("dbfile", nargs="?", type=Path,
                        help="database file to check")
    parser.add_argument("--old-python", default=None,
                        help="interpreter with duckdb 1.x installed")
    args = parser.parse_args(argv)
    dbfile = args.dbfile
    scratch = None
    if dbfile is None:
        scratch = tempfile.TemporaryDirectory()
        dbfile = Path(scratch.name) / "demo.duckdb"
        create_demo_file(dbfile, sys.executable)
    result = report(dbfile, args.old_python)
    print_report(result)
    if scratch is not None:
        scratch.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
