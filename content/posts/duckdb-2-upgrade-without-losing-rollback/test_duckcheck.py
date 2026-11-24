"""Tests for duckcheck.py, the DuckDB 1.x to 2.0 upgrade checker.

Run against the installed DuckDB:
    python3 -m pytest test_duckcheck.py -W error::DeprecationWarning

Cross-version file tests need DUCKDB_OLD_PYTHON pointing at an interpreter
with duckdb 1.x installed; they skip otherwise. No test calls any Arrow
function: on this VM the 2.0.0 Arrow output path crashes the interpreter
(bus error), while the same call works on 1.5.6, so the Arrow API change
is documented from the migration guide, not measured here.
"""

import os
import subprocess
import sys
import threading
from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

import duckcheck

VERSION = duckdb.__version__
LINE = duckcheck.major(VERSION)
OLD_PYTHON = os.environ.get("DUCKDB_OLD_PYTHON")

ROWS = [(1, Decimal("10.50")), (2, Decimal("7.25")), (3, Decimal("11.00"))]
TOTAL = Decimal("28.75")


def new_con():
    return duckdb.connect()


def test_probes_match_installed_version():
    """Every semantics probe returns the value of the installed line.

    merge_double_match is excluded: it differs between 2.0.0 (raises) and
    2.0.1 (silent), so it is covered by test_merge_double_match_reversal
    against the exact installed version instead.
    """
    con = new_con()
    observed = duckcheck.semantics_probes(con)
    for name, expected in duckcheck.EXPECTED.items():
        if name == "merge_double_match":
            continue
        assert observed[name] == expected[LINE], name
    con.close()


def test_merge_double_match_reversal():
    """MERGE double-match: silent on 1.x, raises on 2.0.0, silent on 2.0.1.

    2.0.1 restores the 1.x per-match behavior (#28701). The final value is
    one of the matching source rows, so either is accepted here.
    """
    con = new_con()
    con.execute("CREATE TABLE m_t (id INTEGER PRIMARY KEY, v INTEGER)")
    con.execute("INSERT INTO m_t VALUES (1, 10)")
    con.execute("CREATE TABLE m_s (id INTEGER, v INTEGER)")
    con.execute("INSERT INTO m_s VALUES (1, 20), (1, 30)")
    if VERSION == "2.0.0":
        with pytest.raises(duckdb.InvalidInputException):
            con.execute("MERGE INTO m_t USING m_s ON m_t.id = m_s.id "
                        "WHEN MATCHED THEN UPDATE SET v = m_s.v")
    else:
        con.execute("MERGE INTO m_t USING m_s ON m_t.id = m_s.id "
                    "WHEN MATCHED THEN UPDATE SET v = m_s.v")
        assert con.execute(
            "SELECT v FROM m_t WHERE id = 1").fetchone()[0] in (20, 30)
    con.close()


def test_extension_repository_default():
    """allow_extension_repositories: absent on 1.x, 'undecided' on 2.0.0,
    'hosts' on 2.0.1, where 'undecided' is also rejected outright."""
    con = new_con()
    if LINE == "1.x":
        with pytest.raises(duckdb.CatalogException):
            con.execute(
                "SELECT current_setting('allow_extension_repositories')")
    elif VERSION == "2.0.0":
        assert con.execute(
            "SELECT current_setting('allow_extension_repositories')"
        ).fetchone()[0] == "undecided"
    else:
        assert con.execute(
            "SELECT current_setting('allow_extension_repositories')"
        ).fetchone()[0] == "hosts"
        with pytest.raises(duckdb.InvalidInputException):
            con.execute("SET allow_extension_repositories = 'undecided'")
    con.close()


def test_bridges_restore_old_behavior():
    """On 2.0, every compatibility bridge restores the 1.x behavior."""
    if LINE != "2.0":
        pytest.skip("bridges only exist on DuckDB 2.0")
    con = new_con()
    bridges = duckcheck.check_bridges(con)
    assert bridges, "no bridges reported"
    assert all(bridges.values()), bridges
    con.close()


def test_execute_result_api_removed_on_2():
    """fetch_arrow_table and friends are gone from execute() results on 2.0."""
    con = new_con()
    res = con.execute("SELECT 42 AS x")
    if LINE == "2.0":
        for name in ("fetch_arrow_table", "fetch_record_batch", "arrow", "pl"):
            assert not hasattr(res, name), name
        with pytest.raises(AttributeError):
            res.fetch_arrow_table()
    else:
        for name in ("fetch_arrow_table", "fetch_record_batch", "arrow", "pl"):
            assert hasattr(res, name), name
    res.fetchall()
    con.close()


def test_relation_api_changes():
    """fetchone/fetchmany are gone from relations; iter_rows replaces them."""
    con = new_con()
    rel = con.sql("SELECT * FROM range(3) t(i)")
    if LINE == "2.0":
        with pytest.raises(AttributeError):
            rel.fetchmany(2)
        assert list(rel.iter_rows()) == [(0,), (1,), (2,)]
    else:
        assert rel.fetchmany(2) == [(0,), (1,)]
        with pytest.raises(AttributeError):
            list(rel.iter_rows())
    con.close()


def test_relation_column_named_like_method():
    """rel['offset'] is a column on both lines; rel.offset is a method on 2.0."""
    con = new_con()
    rel = con.sql("SELECT 1 AS offset, 2 AS head")
    assert rel["offset"].fetchall() == [(1,)]
    assert callable(getattr(rel, "offset", None)) == (LINE == "2.0")
    con.close()


def test_write_csv_overwrite_false():
    """overwrite=False raises on 2.0; it silently replaced the file on 1.x."""
    con = new_con()
    path = Path(__file__).parent / "_test_overwrite.csv"
    try:
        con.sql("SELECT 1 AS x").write_csv(str(path))
        if LINE == "2.0":
            with pytest.raises(duckdb.IOException):
                con.sql("SELECT 2 AS x").write_csv(str(path), overwrite=False)
        else:
            con.sql("SELECT 2 AS x").write_csv(str(path), overwrite=False)
            assert con.execute(
                "SELECT * FROM read_csv_auto(?)", [str(path)]
            ).fetchone() == (2,)
    finally:
        path.unlink(missing_ok=True)
    con.close()


def test_sql_of_ddl_returns_relation_on_2():
    """con.sql() of DDL returns None on 1.x and a relation on 2.0."""
    con = new_con()
    result = con.sql("CREATE TABLE ddl_return_check (i INTEGER)")
    assert (result is None) == (LINE == "1.x")
    con.close()


def test_values_non_string_keys_become_map():
    """con.values({1: 'a'}) is a STRUCT on 1.x and a MAP on 2.0."""
    con = new_con()
    rel = con.values({1: "a"})
    assert str(rel.types[0]) == (
        'STRUCT("1" VARCHAR)' if LINE == "1.x" else "MAP(INTEGER, VARCHAR)")
    con.close()


def test_decimal_positive_exponent():
    """Decimal('1E+2') arrives as 1 on 1.x and 100 on 2.0."""
    con = new_con()
    value = con.execute("SELECT ?::DECIMAL", [Decimal("1E+2")]).fetchone()[0]
    assert value == (Decimal("1.000") if LINE == "1.x" else Decimal("100.000"))
    con.close()


def test_open_execute_result_rules():
    """On 2.0, executing another query while an execute() result is
    unfinished raises ResourceInUseException; on 1.x it does not. A
    second execute() replaces the open result, and reading the result
    to its end frees the connection. Merely building a relation with
    con.sql() does not run a query, so it never raises."""
    con = new_con()
    con.execute("CREATE TABLE open_result AS SELECT * FROM range(5) t(i)")
    cur = con.execute("SELECT * FROM open_result")
    if LINE == "2.0":
        with pytest.raises(duckdb.ResourceInUseException):
            con.sql("SELECT 1").fetchall()
        cur.fetchone()
        with pytest.raises(duckdb.ResourceInUseException):
            con.sql("SELECT 1").fetchall()
        cur.fetchall()
        assert con.sql("SELECT 1").fetchall() == [(1,)]
    else:
        assert con.sql("SELECT 1").fetchall() == [(1,)]
    con.close()


def test_complete_frees_the_connection():
    """con.complete() exists on 2.0 and frees the connection after an
    unfinished execute(); it does not exist on 1.x."""
    if LINE == "1.x":
        assert not hasattr(duckdb.connect(), "complete")
        pytest.skip("complete() does not exist on DuckDB 1.x")
    con = new_con()
    con.execute("CREATE TABLE complete_check AS SELECT * FROM range(5) t(i)")
    cur = con.execute("SELECT * FROM complete_check")
    cur.fetchone()
    con.complete()
    assert con.sql("SELECT 1").fetchall() == [(1,)]
    con.close()


def test_one_connection_across_threads():
    """Two threads executing on one connection serialize on 1.x and raise
    ResourceInUseException on 2.0."""
    con = new_con()
    barrier = threading.Barrier(2)
    errors = []

    def worker():
        barrier.wait()
        try:
            con.execute(
                "SELECT sum(i * i) FROM range(50000000) t(i)").fetchall()
        except Exception as exc:  # noqa: BLE001 - the error type is the test
            errors.append(type(exc).__name__)

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if LINE == "2.0":
        assert errors == ["ResourceInUseException"], errors
    else:
        assert errors == [], errors
    con.close()


def _run(python, code):
    proc = subprocess.run([python, "-c", code], capture_output=True,
                          text=True, timeout=120)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _create_file(python, path, compat=False):
    config = (", config={'storage_compatibility_version': 'v1.5.6'}"
              if compat else "")
    code = (
        f"import duckdb; c = duckdb.connect({str(path)!r}{config});"
        "c.execute('CREATE TABLE t (id INTEGER, amount DECIMAL(10, 2))');"
        "c.execute(\"INSERT INTO t VALUES (1, 10.50), (2, 7.25), (3, 11.00)\");"
        "c.close()"
    )
    rc, _, err = _run(python, code)
    assert rc == 0, err


def _open_sum(python, path):
    code = (
        f"import duckdb; c = duckdb.connect({str(path)!r}, read_only=True);"
        "print(c.execute('SELECT count(*), sum(amount) FROM t').fetchone())"
    )
    return _run(python, code)


@pytest.mark.skipif(not OLD_PYTHON, reason="DUCKDB_OLD_PYTHON not set")
@pytest.mark.skipif(LINE != "2.0",
                    reason="cross-version file tests run on DuckDB 2.0 "
                           "against a 1.x interpreter")
class TestCrossVersionFiles:
    """The storage-format one-way door, measured with both interpreters."""

    def test_new_file_unreadable_by_old(self, tmp_path):
        path = tmp_path / "new.duckdb"
        _create_file(sys.executable, path)
        rc, _, err = _open_sum(OLD_PYTHON, path)
        assert rc != 0
        assert "version number 69" in err
        assert "between 64 and 68" in err

    def test_compat_file_readable_by_old(self, tmp_path):
        path = tmp_path / "compat.duckdb"
        _create_file(sys.executable, path, compat=True)
        rc, out, err = _open_sum(OLD_PYTHON, path)
        assert rc == 0, err
        assert out == f"(3, Decimal('{TOTAL}'))"

    def test_old_file_readable_by_new_and_stays_old(self, tmp_path):
        path = tmp_path / "old.duckdb"
        _create_file(OLD_PYTHON, path)
        rc, out, err = _open_sum(sys.executable, path)
        assert rc == 0, err
        assert out == f"(3, Decimal('{TOTAL}'))"
        # The new engine writes to the old file; the old engine must
        # still open it afterwards: the file keeps its storage version.
        code = (
            f"import duckdb; c = duckdb.connect({str(path)!r});"
            "c.execute(\"INSERT INTO t VALUES (4, 5.00)\"); c.close()"
        )
        rc, _, err = _run(sys.executable, code)
        assert rc == 0, err
        rc, out, err = _open_sum(OLD_PYTHON, path)
        assert rc == 0, err
        assert out == "(4, Decimal('33.75'))"

    def test_export_import_roundtrip(self, tmp_path):
        src = tmp_path / "src.duckdb"
        _create_file(OLD_PYTHON, src)
        export_dir = tmp_path / "export"
        dest = tmp_path / "dest.duckdb"
        rc, _, err = _run(OLD_PYTHON,
                          f"import duckdb; c = duckdb.connect({str(src)!r},"
                          f" read_only=True);"
                          f" c.execute(\"EXPORT DATABASE '{export_dir}'\")")
        assert rc == 0, err
        rc, _, err = _run(sys.executable,
                          f"import duckdb; c = duckdb.connect({str(dest)!r});"
                          f" c.execute(\"IMPORT DATABASE '{export_dir}'\")")
        assert rc == 0, err
        rc, out, err = _open_sum(sys.executable, dest)
        assert rc == 0, err
        assert out == f"(3, Decimal('{TOTAL}'))"
