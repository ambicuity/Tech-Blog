"""Tests for poolcheck.py. Run: python3 -m pytest test_poolcheck.py -q"""
import pytest

import poolcheck as pc

TXN = pc.Config(pool_mode="transaction", max_prepared_statements=200,
                version=(1, 26, 0))
TXN_NO_TRACKING = pc.Config(pool_mode="transaction", max_prepared_statements=0,
                            version=(1, 26, 0))
OLD = pc.Config(pool_mode="transaction", max_prepared_statements=200,
                version=(1, 25, 2))
INI = """
[databases]
app = host=127.0.0.1 port=5432 dbname=app

[pgbouncer]
listen_port = 6432
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
max_prepared_statements = 200
server_reset_query_always = 0
"""


def test_parse_version():
    assert pc.parse_version("1.26.0") == (1, 26, 0)
    assert pc.parse_version("1.9") == (1, 9)


def test_load_config_reads_pgbouncer_section_only():
    cfg = pc.load_config(INI)
    assert cfg.pool_mode == "transaction"
    assert cfg.max_prepared_statements == 200
    assert cfg.default_pool_size == 20
    assert cfg.max_client_conn == 1000


def test_protocol_prepared_works_with_tracking():
    v = pc.classify_feature("protocol_prepared_statement", TXN)
    assert v.verdict == pc.WORKS


def test_protocol_prepared_fails_without_tracking():
    v = pc.classify_feature("protocol_prepared_statement", TXN_NO_TRACKING)
    assert v.verdict == pc.SESSION_ONLY


def test_sql_prepare_is_session_only_even_with_tracking():
    # Tracking covers the protocol, not the SQL commands.
    assert pc.classify_feature("sql_prepare", TXN).verdict == pc.SESSION_ONLY


@pytest.mark.parametrize("feature", [
    "listen", "session_advisory_lock", "hold_cursor",
    "temp_table_preserve_rows", "load",
])
def test_session_only_features(feature):
    assert pc.classify_feature(feature, TXN).verdict == pc.SESSION_ONLY


@pytest.mark.parametrize("feature,expected", [
    ("set", pc.USE_LOCAL),
    ("set_local", pc.WORKS),
    ("notify", pc.WORKS),
    ("xact_advisory_lock", pc.WORKS),
    ("cursor_without_hold", pc.WORKS),
    ("temp_table_on_commit_drop", pc.WORKS),
])
def test_transaction_safe_forms(feature, expected):
    assert pc.classify_feature(feature, TXN).verdict == expected


def test_search_path_tracked_on_pg18_with_126():
    v = pc.classify_feature("search_path_set", TXN, pg_version=18)
    assert v.verdict == pc.WORKS


def test_search_path_version_dependent_before_126():
    v = pc.classify_feature("search_path_set", OLD, pg_version=18)
    assert v.verdict == pc.VERSION_DEPENDENT


def test_search_path_version_dependent_on_pg17():
    v = pc.classify_feature("search_path_set", TXN, pg_version=17)
    assert v.verdict == pc.VERSION_DEPENDENT


def test_session_mode_accepts_everything():
    for feature in ["listen", "sql_prepare", "session_advisory_lock"]:
        assert pc.classify_feature(feature, pc.Config(pool_mode="session")).verdict == pc.WORKS


def test_unknown_feature_rejected():
    with pytest.raises(ValueError):
        pc.classify_feature("teleport", TXN)


def test_audit_flags_old_version_for_cves():
    findings = pc.audit(OLD, [])
    assert any(f.rule == "upgrade-pgbouncer" and f.severity == "error" for f in findings)
    assert "CVE-2026-19888" in findings[0].message


def test_audit_clean_for_current_config():
    findings = pc.audit(TXN, ["protocol_prepared_statement", "set_local", "notify"])
    assert findings == []


def test_audit_flags_tracking_off_and_session_only_use():
    findings = pc.audit(TXN_NO_TRACKING, ["protocol_prepared_statement", "listen"])
    rules = {f.rule for f in findings}
    assert "prepared-tracking-off" in rules
    assert "session-only:listen" in rules


def test_audit_warns_on_plain_set_and_reset_always():
    cfg = pc.Config(pool_mode="transaction", server_reset_query_always=1,
                    version=(1, 26, 0))
    rules = {f.rule for f in pc.audit(cfg, ["set"])}
    assert "reset-query-always" in rules
    assert "use-local:set" in rules


def test_audit_warns_when_pool_exceeds_client_cap():
    cfg = pc.Config(pool_mode="transaction", default_pool_size=50,
                    max_client_conn=20, version=(1, 26, 0))
    assert any(f.rule == "pool-larger-than-clients" for f in pc.audit(cfg, []))


def test_pool_tracking_survives_server_rotation():
    pool = pc.Pool(size=3, max_prepared_statements=200)
    pool.prepare("app", "q1", "SELECT * FROM orders WHERE id = $1")
    names = {pool.execute("app", "q1") for _ in range(6)}
    assert names == {"PGBOUNCER_1"}  # one internal name, rewritten everywhere
    assert pool.total_parses() == 3  # prepared once per server, then reused


def test_pool_without_tracking_breaks_on_second_server():
    pool = pc.Pool(size=3, max_prepared_statements=0)
    pool.prepare("app", "q1", "SELECT * FROM orders WHERE id = $1")
    assert pool.execute("app", "q1") == "q1"  # first server holds it
    with pytest.raises(pc.PreparedStatementMissing):
        pool.execute("app", "q1")  # next transaction, different server


def test_pool_same_sql_from_two_clients_shares_internal_name():
    pool = pc.Pool(size=2, max_prepared_statements=200)
    sql = "SELECT * FROM orders WHERE id = $1"
    pool.prepare("app-a", "stmt_a", sql)
    pool.prepare("app-b", "stmt_b", sql)
    assert pool.execute("app-a", "stmt_a") == pool.execute("app-b", "stmt_b")


def test_pool_lru_eviction_forces_reprepare():
    pool = pc.Pool(size=1, max_prepared_statements=2)
    for i in range(3):
        pool.prepare("app", f"q{i}", f"SELECT {i}")
    pool.execute("app", "q0")
    pool.execute("app", "q1")
    pool.execute("app", "q2")  # evicts q0 from the single server
    assert pool.total_parses() == 3
    pool.execute("app", "q0")  # evicted, so it is prepared again
    assert pool.total_parses() == 4


def test_pool_execute_unprepared_raises():
    pool = pc.Pool(size=1, max_prepared_statements=200)
    with pytest.raises(pc.PreparedStatementMissing):
        pool.execute("app", "never_prepared")


def test_pool_rejects_zero_size():
    with pytest.raises(ValueError):
        pc.Pool(size=0, max_prepared_statements=200)
