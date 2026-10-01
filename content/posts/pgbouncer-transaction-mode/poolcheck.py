"""Check a PgBouncer setup for transaction-pooling mistakes.

Targets PgBouncer 1.26 and PostgreSQL 18. The module does two jobs:

1. classify_feature() / audit() apply the documented pooling rules to the
   features an application uses and to a parsed pgbouncer.ini, and report
   what breaks in transaction mode and why.
2. Pool is a small, faithful model of PgBouncer's protocol-level prepared
   statement tracking (max_prepared_statements): client statement names are
   rewritten to internal PGBOUNCER_<id> names, a statement is prepared on a
   server connection only if it is not already there, and each server keeps
   an LRU cache bounded by max_prepared_statements. With tracking disabled
   (max_prepared_statements = 0) the model reproduces the classic failure:
   a later transaction lands on a different server and the statement is
   missing there.

The model is deliberately small. It models assignment, prepared-statement
placement and eviction; it does not model the wire protocol.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field

# PgBouncer versions that matter for the rules below.
PREPARED_TRACKING_SINCE = (1, 21)   # feature added, opt-in
PREPARED_DEFAULT_ON_SINCE = (1, 24)  # max_prepared_statements defaults to 200
SEARCH_PATH_TRACKED_SINCE = (1, 26)  # search_path tracked on PostgreSQL 18+
SECURITY_FIX_VERSION = (1, 26, 0)   # CVE-2026-19888, CVE-2026-6668, CVE-2026-6669


def parse_version(text: str) -> tuple[int, ...]:
    """Parse '1.26.0' into (1, 26, 0). Raises ValueError on junk."""
    parts = tuple(int(p) for p in text.strip().split("."))
    if not parts:
        raise ValueError("empty version")
    return parts


@dataclass(frozen=True)
class Config:
    """The pgbouncer.ini settings this checker reasons about."""

    pool_mode: str = "session"
    max_prepared_statements: int = 200
    default_pool_size: int = 20
    max_client_conn: int = 100
    server_reset_query_always: int = 0
    track_extra_parameters: tuple[str, ...] = ()
    version: tuple[int, ...] = (1, 26, 0)


def load_config(text: str, version: str = "1.26.0") -> Config:
    """Parse the [pgbouncer] section of an ini file (the subset we check).

    Only simple ``key = value`` lines are read; per-database and per-user
    overrides are out of scope, so audit the effective global config.
    """
    values: dict[str, str] = {}
    section = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith((";", "#")):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip().lower()
            continue
        if section == "pgbouncer" and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip().lower()] = value.strip()

    def as_int(key: str, default: int) -> int:
        try:
            return int(values[key])
        except (KeyError, ValueError):
            return default

    tracked = tuple(
        p.strip() for p in values.get("track_extra_parameters", "").split(",") if p.strip()
    )
    return Config(
        pool_mode=values.get("pool_mode", "session").lower(),
        max_prepared_statements=as_int("max_prepared_statements", 200),
        default_pool_size=as_int("default_pool_size", 20),
        max_client_conn=as_int("max_client_conn", 100),
        server_reset_query_always=as_int("server_reset_query_always", 0),
        track_extra_parameters=tracked,
        version=parse_version(version),
    )


# Verdicts returned by classify_feature().
WORKS = "works"                # safe in transaction mode as written
USE_LOCAL = "use_local"        # works only in the transaction-scoped form
SESSION_ONLY = "session_only"  # needs session pooling (or a direct connection)
VERSION_DEPENDENT = "version_dependent"  # answer depends on the versions pinned


@dataclass(frozen=True)
class Verdict:
    verdict: str
    reason: str


# The feature map in PgBouncer's own documentation (features.html) is the
# authority for this table; the notes say what to do instead.
def classify_feature(feature: str, config: Config, pg_version: int = 18) -> Verdict:
    """Classify one PostgreSQL feature for transaction pooling."""
    if config.pool_mode == "session":
        return Verdict(WORKS, "session pooling keeps one server for the whole session")
    if config.pool_mode == "statement":
        if feature in {"multi_statement_transaction"}:
            return Verdict(SESSION_ONLY, "statement pooling disallows multi-statement transactions")
        # Everything below is at least as strict as transaction mode.
    table: dict[str, Verdict] = {
        "protocol_prepared_statement": (
            Verdict(WORKS, "PgBouncer tracks and re-prepares it on the assigned server")
            if config.max_prepared_statements > 0
            else Verdict(SESSION_ONLY, "max_prepared_statements = 0 disables tracking; "
                                       "the next transaction may land on a server without it")
        ),
        "sql_prepare": Verdict(SESSION_ONLY, "SQL PREPARE/EXECUTE/DEALLOCATE are forwarded "
                                             "untracked; the docs list them as never working "
                                             "in transaction pooling"),
        "set": Verdict(USE_LOCAL, "plain SET outlives the transaction on the server and can "
                                  "leak to the next client; use SET LOCAL inside the transaction"),
        "set_local": Verdict(WORKS, "SET LOCAL ends with the transaction, so pooling cannot leak it"),
        "listen": Verdict(SESSION_ONLY, "LISTEN needs the same server connection for the whole "
                                        "session; a pooled client is not attached between transactions"),
        "notify": Verdict(WORKS, "NOTIFY is listed as working in transaction pooling"),
        "session_advisory_lock": Verdict(SESSION_ONLY, "pg_advisory_lock is held by a session; "
                                                       "the session changes at transaction end"),
        "xact_advisory_lock": Verdict(WORKS, "pg_advisory_xact_lock is released at transaction "
                                             "end, which matches the pooling boundary"),
        "hold_cursor": Verdict(SESSION_ONLY, "WITH HOLD cursors outlive their transaction, "
                                             "which transaction pooling cannot promise"),
        "cursor_without_hold": Verdict(WORKS, "a cursor closed by transaction end stays inside "
                                              "one assignment"),
        "temp_table_on_commit_drop": Verdict(WORKS, "ON COMMIT DROP temp tables end with the "
                                                    "transaction that created them"),
        "temp_table_preserve_rows": Verdict(SESSION_ONLY, "a temp table that must keep rows "
                                                          "across transactions needs one session"),
        "load": Verdict(SESSION_ONLY, "LOAD is listed as never working in transaction pooling"),
    }
    if feature == "search_path_set":
        if pg_version >= 18 and config.version >= SEARCH_PATH_TRACKED_SINCE:
            return Verdict(WORKS, "PgBouncer 1.26 tracks search_path by default on "
                                  "PostgreSQL 18+, restoring it per client")
        return Verdict(VERSION_DEPENDENT, "before PgBouncer 1.26 on PostgreSQL 18 (or on older "
                                          "PostgreSQL), SET search_path is only tracked from the "
                                          "startup packet; a later SET can leak. Prefer SET LOCAL")
    if feature in table:
        return table[feature]
    raise ValueError(f"unknown feature: {feature!r}")


@dataclass(frozen=True)
class Finding:
    severity: str  # "error" or "warning"
    rule: str
    message: str


def audit(config: Config, features_used: list[str], pg_version: int = 18) -> list[Finding]:
    """Audit a config plus the features the application actually uses."""
    findings: list[Finding] = []
    if config.version < SECURITY_FIX_VERSION:
        findings.append(Finding(
            "error", "upgrade-pgbouncer",
            "PgBouncer before 1.26.0 is exposed to CVE-2026-19888 (unauthenticated "
            "SCRAM crash), CVE-2026-6668 (packet-buffer hang) and CVE-2026-6669 "
            "(unbounded SCRAM iterations). Upgrade to 1.26.0 or later."))
    if config.pool_mode == "transaction":
        if config.max_prepared_statements == 0 and "protocol_prepared_statement" in features_used:
            findings.append(Finding(
                "error", "prepared-tracking-off",
                "The application uses protocol-level prepared statements but "
                "max_prepared_statements = 0 disables tracking. Set it at or above "
                "the number of distinct queries the application prepares (default 200)."))
        if config.server_reset_query_always:
            findings.append(Finding(
                "warning", "reset-query-always",
                "server_reset_query_always in transaction mode turns non-deterministic "
                "session-state breakage into deterministic breakage: clients always lose "
                "state after each transaction. Fix the application instead."))
        for feature in features_used:
            verdict = classify_feature(feature, config, pg_version)
            if verdict.verdict == SESSION_ONLY:
                findings.append(Finding(
                    "error", f"session-only:{feature}",
                    f"{feature} needs a session: {verdict.reason}. Route that work to a "
                    "session-mode pool or a direct connection."))
            elif verdict.verdict == USE_LOCAL:
                findings.append(Finding(
                    "warning", f"use-local:{feature}",
                    f"{feature}: {verdict.reason}."))
    if config.default_pool_size > config.max_client_conn:
        findings.append(Finding(
            "warning", "pool-larger-than-clients",
            "default_pool_size exceeds max_client_conn; the pool can never be the "
            "bottleneck you sized it to be. Size the pool from server capacity, "
            "not from the client count."))
    return findings


class PreparedStatementMissing(Exception):
    """A client executed a statement the assigned server does not hold."""


@dataclass
class Server:
    """One PostgreSQL server connection behind the pool."""

    name: str
    prepared: OrderedDict[str, str] = field(default_factory=OrderedDict)  # internal name -> SQL
    parses: int = 0  # times this server had to prepare (parse) a statement


class Pool:
    """A transaction-mode pool with PgBouncer-style statement tracking.

    Each execute() call is one transaction: the pool assigns the
    least-recently-used server, runs the call, and releases the server.
    """

    def __init__(self, size: int, max_prepared_statements: int) -> None:
        if size < 1:
            raise ValueError("pool size must be at least 1")
        self.servers = [Server(f"s{i + 1}") for i in range(size)]
        self.max_prepared = max_prepared_statements
        self._internal: dict[str, str] = {}  # SQL -> internal name
        self._client_names: dict[tuple[str, str], str] = {}  # (client, name) -> SQL
        self._counter = 0
        self._rotation = 0

    def _assign(self) -> Server:
        server = self.servers[self._rotation % len(self.servers)]
        self._rotation += 1
        return server

    def prepare(self, client: str, name: str, sql: str) -> None:
        """Record a client-side Prepare; the server work happens at execute."""
        self._client_names[(client, name)] = sql

    def execute(self, client: str, name: str) -> str:
        """Execute a prepared statement in a new transaction.

        Returns the internal name used on the server. Raises
        PreparedStatementMissing when tracking is disabled and the assigned
        server never prepared the statement.
        """
        try:
            sql = self._client_names[(client, name)]
        except KeyError:
            raise PreparedStatementMissing(
                f"client {client} never prepared {name!r}") from None
        server = self._assign()
        if self.max_prepared == 0:
            # No tracking: the statement exists only where the client happened
            # to prepare it, which this model treats as the first server.
            if server is not self.servers[0]:
                raise PreparedStatementMissing(
                    f"prepared statement \"{name}\" does not exist on {server.name}")
            return name
        internal = self._internal.get(sql)
        if internal is None:
            self._counter += 1
            internal = f"PGBOUNCER_{self._counter}"
            self._internal[sql] = internal
        if internal in server.prepared:
            server.prepared.move_to_end(internal)
        else:
            server.parses += 1
            server.prepared[internal] = sql
            while len(server.prepared) > self.max_prepared:
                server.prepared.popitem(last=False)  # evict least recently used
        return internal

    def total_parses(self) -> int:
        return sum(s.parses for s in self.servers)
