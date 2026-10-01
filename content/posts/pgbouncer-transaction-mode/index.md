---
title: "PgBouncer Transaction Mode: What Still Needs a Session"
description: >-
  Prepared statements now work in PgBouncer transaction mode, and 1.26
  tracks search_path on PostgreSQL 18. What still needs a session, checked.
date: 2026-10-01 15:00:00 +0000
author: ritesh
categories: [Database, Reliability]
tags: [pgbouncer, postgresql, connection-pooling, prepared-statements, transactions]
kind: Guide
draft: false
cover:
  image: cover.webp
  alt: Many client connections entering a PgBouncer pool in transaction mode and leaving through a small number of PostgreSQL server connections, with a prepared statement re-prepared on a second server.
---

Most teams adopt PgBouncer in transaction mode for one reason: a few dozen PostgreSQL connections should serve hundreds of application clients, because each client only needs a server for the duration of one transaction. Then the old advice arrives. Turn off prepared statements. Never use `SET`. Expect strange, occasional failures that nobody can reproduce. Some of that advice was correct in 2020. Some of it is still correct today, and mixing the two up is how teams either give up pooling benefits they could keep, or ship session-state bugs that only appear under the wrong connection assignment.

This guide separates the two against current versions: PostgreSQL 18.6 and PgBouncer 1.26.0, released 2026-09-23. Protocol-level prepared statements have worked in transaction mode since PgBouncer 1.21 and have been on by default since 1.24. PgBouncer 1.26 now tracks `search_path` on PostgreSQL 18, so another long-standing leak is closed. What remains genuinely session-only is a short, specific list, and for most of it there is a transaction-scoped replacement. The code is Python 3.12, standard library only, and ships next to this article with its tests: a checker that classifies features and audits a `pgbouncer.ini`, plus a small model of PgBouncer's prepared-statement tracking that reproduces both the old failure and the current behaviour.

> [!NOTE]
> **In short**
> - Upgrade to PgBouncer 1.26.0 first. Versions before it carry three remotely triggerable security fixes, two of them reachable without authenticating.
> - Keep protocol-level prepared statements on: `max_prepared_statements` defaults to 200, and PgBouncer re-prepares a statement transparently when a transaction lands on a server that does not have it yet. SQL `PREPARE` is a different feature and is still not tracked.
> - Plain `SET` is still the wrong tool in transaction mode. Use `SET LOCAL`, which ends with the transaction. On PostgreSQL 18 with PgBouncer 1.26, `search_path` is now tracked per client, but that covers one parameter, not the pattern.
> - `LISTEN`, session advisory locks, `WITH HOLD` cursors and temp tables that keep rows across transactions still need a session. Route that work to a session-mode pool or a direct connection instead of abandoning transaction mode for everything.
> - Every rule in this article is encoded in [poolcheck.py](poolcheck.py) and proved by [test_poolcheck.py](test_poolcheck.py), so a code review can run the argument instead of trusting it.

## First, run PgBouncer 1.26

The pooling rules below only matter on a version that is safe to expose. PgBouncer 1.26.0 (2026-09-23) fixes three security issues in the changelog:

- CVE-2026-19888: before 1.26.0, PgBouncer did not check that the SCRAM client-final-message contained a nonce. An unauthenticated remote attacker could crash PgBouncer by sending one without a nonce, including for users that do not exist. The bug dates back to SCRAM support in 1.11.0.
- CVE-2026-6668: an integer overflow in packet buffer growth could hang PgBouncer in an infinite loop, again reachable without authenticating when `max_packet_size` is at its default. Because PgBouncer is single-threaded, the hang stops it serving any client until the process is killed.
- CVE-2026-6669: the SCRAM iteration count accepted from a server was unbounded, so a malicious or compromised PostgreSQL server could make PgBouncer do unbounded work during one login. The count is now capped at 1000000.

1.26 also removes the deprecated online restart (`-R`) takeover functionality, together with the `SHOW FDS` and `SUSPEND` admin commands that existed only to support it; the changelog points to rolling restarts with `so_reuseport` instead. If your upgrade scripts or systemd units still rely on `-R`, the upgrade is the moment they break, so check before you roll it out, not after.

## The one rule behind every failure

In transaction mode a server connection is assigned to a client only during a transaction. When PgBouncer sees the transaction end, the server goes back into the pool. The next transaction from the same client can be assigned a different server, and another client's transaction can take the server you just used.

![A client transaction is assigned server s1. At commit, s1 returns to the PgBouncer pool. Another client's transaction takes s1 next, and the first client's following transaction lands on s2 instead.](pool-flow.svg "Transaction pooling: the assignment boundary is the transaction, so nothing stored in the session survives it by design."){: .figure}

That single rule predicts everything else in this article. Any feature whose state lives in the session and must survive a transaction boundary is incompatible, unless PgBouncer explicitly tracks that state and restores it per client. Prepared statements and a defined set of parameters are now tracked. Session locks, listeners and cursors are not, because there is no meaningful way to move them between servers mid-session.

The same boundary is why transaction mode pairs well with designs that keep each unit of work inside one transaction, such as writing a business row and its [transactional outbox](/posts/transactional-outbox-reliable-events-without-dual-writes/) event together: the pool never has to guess where one unit ends and the next begins.

## Prepared statements: the workaround you can delete

The classic transaction-mode failure is `prepared statement "q1" does not exist`. A driver prepares a statement on one server connection, the transaction ends, and the next transaction lands on a server that has never seen that name. For years the standard fix was to disable prepared statements in the driver and pay the extra parse and plan cost on every query.

That fix is obsolete on a current PgBouncer, for protocol-level prepared statements:

- 1.21.0 (2023-10-16) added tracking of protocol-level named prepared statements, initially opt-in through the new `max_prepared_statements` setting.
- 1.22.0 added support for `DEALLOCATE ALL` and `DISCARD ALL` while tracking is on; a normal `DEALLOCATE` is still unsupported.
- 1.24 enabled the feature by default: `max_prepared_statements` defaults to 200.
- 1.26 sends `pgbouncer.max_prepared_statements` (alongside `pgbouncer.version` and `pgbouncer.pool_mode`) as a `ParameterStatus` message at login, so a driver or a diagnostic script can detect the pooler and its setting instead of guessing from the error stream.

The mechanism, from the PgBouncer configuration documentation: PgBouncer examines the queries clients send as prepared statements and gives each unique query string an internal name of the form `PGBOUNCER_{unique_id}`. Identical SQL from different clients shares one internal name. PgBouncer records the name each client used, rewrites commands to the internal name, and if the statement is not yet prepared on the server assigned to this transaction, it prepares it there first, transparently. The value of `max_prepared_statements` is the size of the per-server LRU cache of active statements; 0 disables the feature entirely.

![A client prepares q1. PgBouncer rewrites it to the internal name PGBOUNCER_1 and records the mapping in its statement cache. The statement executes on server s1, which now holds it. The client's next transaction lands on s2, where PgBouncer prepares PGBOUNCER_1 before executing it, so the client sees no error.](prepared-tracking.svg "Prepared-statement tracking: one internal name per unique SQL string, re-prepared on whichever server a transaction is assigned."){: .figure}

Two limits matter in practice. First, sizing: keep `max_prepared_statements` at or above the number of distinct queries the application actually prepares, or hot statements will be evicted from a server's LRU cache and re-parsed repeatedly. The documentation notes the cost side of raising it: more memory per server connection on PostgreSQL, plus PgBouncer's own tracking and packet-rewriting CPU. Second, type stability: if the same SQL string is executed with different argument or result types, PostgreSQL can raise `cached plan must not change result type`. The documentation calls out DDL migrations as the common trigger; the operational fix is to run `RECONNECT` on the PgBouncer admin console after the migration so statements are re-prepared. That pairs with running the migration itself over a direct connection, the same separation most teams already use for tools such as [database migrations with Flyway](/posts/automating-database-migrations-with-flyway-and-docker-a-practical-guide/).

> [!WARNING]
> Tracking covers the wire protocol, not the SQL commands. `PREPARE`, `EXECUTE` and `DEALLOCATE` written as SQL are forwarded straight to PostgreSQL, untracked, and PgBouncer's feature map lists them as never working in transaction pooling. An application (or an ORM mode) that prepares through SQL statements instead of the protocol still needs session mode.

## Session state: `SET`, and the `search_path` change in 1.26

PgBouncer's feature map is blunt about `SET` in transaction pooling: never. A plain `SET` changes the server session, the transaction ends, the server returns to the pool with your setting still applied, and the next client assigned that server inherits it. `SET work_mem = '256MB'` for one reporting query becomes every later client's `work_mem` until something resets it, and the failure is silent: queries still return correct results, just with someone else's resource settings, locale or timeout.

![Three rows over one server connection. First, an untracked SET by client A survives commit and is inherited by client B. Second, a parameter PgBouncer tracks is recorded per client and restored, so B sees its own value. Third, SET LOCAL applies only inside A's transaction and ends at commit on any version.](session-state.svg "The leak, the tracked exception, and the form that is always safe: SET LOCAL."){: .figure}

The correction is not to avoid settings; it is to scope them. `SET LOCAL` applies inside the current transaction only and ends when it ends, which is exactly the pooling boundary. The checker encodes the pair as two different features for that reason: `set` is classified `use_local`, and `set_local` is classified `works`.

There is a real, narrower exception, and 1.26 widened it. PgBouncer tracks the parameters PostgreSQL reports to the client by default, restoring each client's values when it becomes active on a server. The configuration documentation lists the default tracked set, which now includes `search_path` on PostgreSQL 18 and later and `default_transaction_read_only` on PostgreSQL 14 and later; 1.26's headline feature is exactly this: track all parameters PostgreSQL reports by default, most notably `search_path`. So on PostgreSQL 18 with PgBouncer 1.26, a client that runs `SET search_path = tenant_a` no longer leaks that schema to the next client.

Read the limits before relying on it. On PostgreSQL before 18, the server does not report `search_path`, so PgBouncer only knows the value from the client's startup packet; a `SET` issued later is not tracked and can still leak. Additional parameters can be tracked with `track_extra_parameters`, but only parameters PostgreSQL reports. The pattern to teach is therefore unchanged: tracked parameters are a safety net for a defined list, and `SET LOCAL` is the rule for anything you set deliberately inside a transaction.

One related setting deserves a warning label. `server_reset_query` is not used in transaction mode, by design: pooled clients must not depend on session state for a reset query to clean up. Setting `server_reset_query_always = 1` forces it anyway, and the documentation describes the result precisely: it changes non-deterministic breakage into deterministic breakage, because clients then always lose state after each transaction. If a team reaches for it, the application is using session features it should stop using; the checker flags it as a warning rather than letting it look like a fix.

## What still needs a session, and what to use instead

Everything below comes from PgBouncer's published feature map for transaction pooling, cross-checked against the configuration documentation. "Never" is the documentation's own word for these rows.

| Feature | Transaction mode | Use instead |
| :--- | :--- | :--- |
| Protocol-level prepared statements | Works, with `max_prepared_statements > 0` | Nothing to change; keep driver prepared statements on |
| SQL `PREPARE` / `EXECUTE` / `DEALLOCATE` | Never | Protocol-level preparation, or session mode for that workload |
| `SET` | Never (leaks to the next client) | `SET LOCAL`; rely on tracking only for the documented parameters |
| `LISTEN` | Never | A dedicated direct or session-mode connection for the listener; `NOTIFY` itself works |
| Session advisory locks (`pg_advisory_lock`) | Never | `pg_advisory_xact_lock`, released at transaction end; or an external lock service when the lock must outlive a transaction |
| `WITH HOLD` cursors | Never | A cursor closed by transaction end, or materialise the result set inside the transaction |
| Temp tables, `ON COMMIT DROP` | Works | Nothing to change |
| Temp tables that preserve rows across transactions | Never | A regular (possibly unlogged) table keyed by a run or session ID, with cleanup |
| `LOAD` | Never | Session mode for the rare session that needs it |
| Multi-statement transactions | Works in transaction mode; disallowed in statement mode | Keep statement mode for autocommit-only workloads, as documented |

Notice the shape of the right-hand column: almost every "never" has a transaction-scoped form or a small, separate session-mode path. The production layout that follows is two pools with intent: transaction mode for request traffic, and a small session-mode pool (or direct connections) reserved for listeners, migration tooling and administrative work. That is a routing decision in configuration, not a reason to run everything in session mode and lose the multiplexing.

## Failure modes

| Failure | What the reader sees | Cause | Fix |
| :--- | :--- | :--- | :--- |
| Prepared statement missing | `prepared statement "q1" does not exist`, intermittently | Tracking disabled (`max_prepared_statements = 0`), an old PgBouncer, or SQL-level `PREPARE` | Run 1.26 with the default 200; use protocol-level preparation |
| Leaked session setting | Wrong schema, locale or resource limits for unrelated requests | Plain `SET` survived on a pooled server; on older PostgreSQL, an untracked `search_path` change | `SET LOCAL`; upgrade for tracked `search_path` on PostgreSQL 18 |
| Listener goes silent | `NOTIFY` events never arrive, no error | `LISTEN` registered on a session the client no longer holds | Give the listener its own session-mode or direct connection |
| Lock that does not lock | Two workers enter a critical section | A session advisory lock was released or moved when the assignment changed | `pg_advisory_xact_lock` inside the transaction that does the work |
| Cursor or temp data vanishes | `cursor does not exist`, or an empty temp table in the next transaction | State was stored past the transaction boundary | Keep the cursor's life inside one transaction; use `ON COMMIT DROP` or a real table |
| Pooler down or stalled for everyone | All clients fail to connect or hang at once | Pre-1.26 PgBouncer exposed to the SCRAM crash or packet-buffer hang | Upgrade to 1.26.0; the fixes are listed in the changelog |
| Stale prepared plan after a migration | `cached plan must not change result type` | A prepared statement kept its old result type across a DDL change | `RECONNECT` on the admin console after the migration |

## Proving it: the checker and the pool model

Two programs ship with this article. [poolcheck.py](poolcheck.py) holds the rules: `classify_feature()` maps each feature above to `works`, `use_local`, `session_only` or `version_dependent` for a given configuration and PostgreSQL version, and `audit()` turns a parsed `pgbouncer.ini` plus the list of features an application uses into findings, including the pre-1.26 upgrade error. [test_poolcheck.py](test_poolcheck.py) runs 32 tests against it; all pass on Python 3.12.

The second half of the file is the part worth reading closely: a `Pool` model of statement tracking. Each `execute()` call is one transaction on the least-recently-used server. With tracking on, identical SQL from two different clients resolves to one internal name, a statement is parsed once per server and then reused, and evicting it from a server's LRU cache forces exactly one re-prepare on next use:

```python
def test_pool_tracking_survives_server_rotation():
    pool = pc.Pool(size=3, max_prepared_statements=200)
    pool.prepare("app", "q1", "SELECT * FROM orders WHERE id = $1")
    names = {pool.execute("app", "q1") for _ in range(6)}
    assert names == {"PGBOUNCER_1"}  # one internal name, rewritten everywhere
    assert pool.total_parses() == 3  # prepared once per server, then reused
```

With tracking disabled, the same model reproduces the production failure deterministically: the first transaction succeeds on the server that holds the statement, and the next transaction, assigned a different server, raises `PreparedStatementMissing`. That asymmetry is the article's central claim in executable form: the error was never a property of prepared statements, it was a property of untracked statements crossing an assignment boundary.

```bash
python3 -m pytest test_poolcheck.py -q
```

The model is a model: it reproduces assignment, naming, placement and eviction as documented, and deliberately does not implement the wire protocol. The version-dependent claims (default 200, the 1.26 tracking list, the three CVEs) are not modelled; they are cited from the changelog and configuration documentation in the references.

## Operating it

Connect to the admin console as an `admin_users` or `stats_users` account on the special `pgbouncer` database and watch the pool, not the process:

```sql
SHOW POOLS;    -- per pool: clients active and waiting, servers active and idle
SHOW STATS;    -- per database: queries, transactions, wait time, prepared-statement counters
SHOW SERVERS;  -- the actual PostgreSQL connections behind the pool
SHOW CONFIG;   -- confirm pool_mode and max_prepared_statements are what you deployed
SHOW VERSION;  -- confirm the binary is 1.26.0 or later
```

The numbers to alert on are `cl_waiting` in `SHOW POOLS` (clients queued because every server is busy: either the pool is too small for the transaction rate, or transactions are being held open too long) and the average wait time in `SHOW STATS` (the same queue, seen as latency). Treat a rising wait queue as a transaction-duration problem first and a pool-size problem second: doubling `default_pool_size` in front of a PostgreSQL that is already saturated moves the queue from PgBouncer to the database, where it is more expensive. Size the pool from server capacity, in the same spirit as sizing [Kubernetes resource requests and limits](/posts/kubernetes-resource-requests-and-limits-masterclass/) from measured use rather than from the number of callers. After any DDL migration that changes a prepared query's result type, run `RECONNECT` and watch for the cached-plan error disappearing from the log.

## Trade-offs and alternatives

- **Session mode for everything.** Correct for every feature, and sometimes the right answer for a small, stateful workload. The cost is the thing PgBouncer exists to remove: one server connection per client for the client's whole lifetime, so connection count, not transaction rate, sizes your database.
- **Statement mode.** The most aggressive pooling: the server is released after each statement, and multi-statement transactions are disallowed. It fits genuinely autocommit-only workloads and breaks anything that needs even a two-statement transaction, so it is a niche, not a default.
- **Driver or application-side pooling only.** Keeps every feature and avoids a hop, but pools do not compose across processes or languages: ten services with a pool of twenty each are two hundred server connections, and no single place can enforce a global limit. A central PgBouncer in transaction mode is the usual answer once more than one process talks to the same database.
- **No pooler.** Defensible for one small service against one database. It stops being defensible at the first connection storm, deploy overlap or second service, which is when teams adopt PgBouncer in a hurry and inherit the folklore this article is trying to retire.

My recommendation: transaction mode as the default pool for request traffic on PgBouncer 1.26, prepared statements left on, `SET LOCAL` as a lintable rule, and a deliberately small session-mode path for listeners, locks that must outlive a transaction, and migrations.

## Checklist

- [ ] PgBouncer is 1.26.0 or later (`SHOW VERSION`), and nothing in the deployment still relies on the removed `-R` online restart.
- [ ] `pool_mode = transaction` for request traffic, with a separate session-mode or direct path for listeners and migrations.
- [ ] `max_prepared_statements` is at or above the number of distinct prepared queries (default 200), and drivers keep protocol-level prepared statements enabled.
- [ ] No SQL-level `PREPARE` in pooled code paths.
- [ ] Every deliberate setting inside a transaction uses `SET LOCAL`; tracked parameters are treated as a safety net, not the mechanism.
- [ ] Session advisory locks are replaced by `pg_advisory_xact_lock`, or the work is routed to the session pool.
- [ ] Alerts exist on `cl_waiting` and average wait time; after DDL changes, `RECONNECT` is part of the migration runbook.

## References

- PgBouncer, [Changelog (1.26.0 security fixes and search_path tracking; 1.24 default prepared statements; 1.21 feature introduction)](https://www.pgbouncer.org/changelog.html)
- PgBouncer, [Configuration (pool_mode, max_prepared_statements, tracked parameters, server_reset_query_always)](https://www.pgbouncer.org/config.html)
- PgBouncer, [Features and SQL feature map for pooling modes](https://www.pgbouncer.org/features.html)
- PgBouncer, [Usage and the admin console](https://www.pgbouncer.org/usage.html)
- PostgreSQL documentation, [SET and SET LOCAL](https://www.postgresql.org/docs/current/sql-set.html)
- PostgreSQL documentation, [PREPARE](https://www.postgresql.org/docs/current/sql-prepare.html)
- PostgreSQL documentation, [Advisory lock functions](https://www.postgresql.org/docs/current/functions-admin.html)
- PostgreSQL documentation, [Explicit locking, including advisory locks](https://www.postgresql.org/docs/current/explicit-locking.html)
