---
title: "Upgrading to DuckDB 2.0 Without Losing Your Rollback"
description: >-
  DuckDB 2.0.0 writes storage format v69, which no pre-2.0 version can read.
  How to upgrade a fleet without stranding it, and how to catch the silent
  result changes before your queries do.
date: 2026-11-19 15:00:00 +0000
author: ritesh
categories: [Database, Reliability]
tags: [duckdb, upgrades, migrations, python, storage]
kind: Guide
draft: false
cover:
  image: cover.webp
  alt: A database file crossing a one-way door from DuckDB 1.5 to DuckDB 2.0, with the old version locked out on the far side.
---

DuckDB 2.0.0 LTS, released on 2026-10-21, is the project's biggest feature release so far, built from close to 20,000 commits since DuckDB 1.5. It also moves the storage format forward, and that move is one-way. A file created by 2.0.0 uses storage version 69, and no DuckDB before 2.0 can open it: the old process dies at open time with an IO Error. Upgrade one process in a fleet that shares a file, and the first new file it creates is in a format the rest of the fleet cannot read. Your rollback is gone the moment the new file exists.

This article targets **DuckDB 2.0.0 LTS and DuckDB 1.5.6, Python 3.12**. Every behavior below was measured on both versions in this run, side by side, with the probe harness shipped next to the article. Two exceptions are stated where they happen: the Arrow output path and the Quack server could not run in this VM, so those sections describe what the documentation says and say so. DuckDB 2.0.1 is due 2026-11-20 (tentative; it slipped from 2026-11-18), and DuckDB 1.4 LTS reached end of life on 2026-11-17. DuckDB 1.5 support was extended to March 2027, so staying on 1.5 while you prepare is a supported choice, not a stall.

> [!NOTE]
> **In short**
> - A 2.0.0 process that creates a file writes storage version 69, which no pre-2.0 process can open. A 2.0.0 process that opens an old file keeps the old storage version, so the file stays readable.
> - Upgrade one process at a time and you strand the rest: the first new file a 2.0.0 process creates is the point of no return.
> - Several expressions return different results on 2.0.0 with no error: the `~` regex operator, the `!` factorial operator, `X'...'` and `B'...'` literals, and untyped `NULL` columns. Re-run your real queries and diff the results.
> - Keep a pre-upgrade copy of every file, and write new files with an explicit storage version while any 1.x process remains. The `duckcheck.py` harness shipped with this article reports which side of the door each file sits on.

## The one-way door

DuckDB is an in-process database: the library is the database, and the file is the state. There is no server to upgrade first. Each process opens the file with the version it was built against, and the version that writes the file decides what every other process can do with it.

The rule, from the [migration guide](https://duckdb.org/docs/2.0/operations_manual/migration), is short: versions before 2.0.0 cannot read files that use the 2.0.0 storage format, and by default every new file created by v2.0.0 uses it (storage version 69). The other direction keeps working: 2.0.0 can read and write existing files created by earlier versions, and those files keep their storage version when 2.0.0 writes to them, so they remain readable by the earlier version.

That asymmetry is the whole upgrade problem. "2.0 can read old files" sounds like a rollback, and it is not one: reading an old file is safe, creating a new file closes the door. The migration guide warns that in a deployment with many processes on different versions, a file created by a v2.0.0 process is unreadable by the remaining older processes.

I measured the four cases with a three-row file (sum 28.75) and two interpreters, duckdb 1.5.6 and duckdb 2.0.0:

| File | Opened by 1.5.6 | Opened by 2.0.0 |
| :--- | :--- | :--- |
| Created by 1.5.6 | yes, sum 28.75 | yes, sum 28.75 |
| Created by 1.5.6, then one row added by 2.0.0 | yes, sum 33.75, 4 rows | yes |
| Created by 2.0.0, default storage | **no**: IO Error, "Trying to read a database file with version number 69, but we can only read versions between 64 and 68." | yes, sum 28.75 |
| Created by 2.0.0 with `storage_compatibility_version = 'v1.5.6'` | yes, sum 28.75 | yes, sum 28.75 |

The second row saves rollbacks: a 2.0.0 process can write to a 1.5.6 file all day and the file stays readable, because it keeps its storage version. The third row ends them: the moment any 2.0.0 process creates a fresh file, or you migrate one to v69, the only way back is the pre-upgrade copy or a data round trip.

![A 1.5.6 file stays version 68 when 2.0.0 writes to it, so 1.5.6 still opens it; a new 2.0.0 file is version 69, which 1.5.6 cannot open.](storage-door.svg "A 2.0.0 process can write to an old file without closing the door; creating a new file closes it."){: .figure}

No SQL query reports a file's storage version, so record the creator version when a file is made and check readability directly. That is what the harness in this article does: it opens the file with both interpreters and reports which side of the door it sits on.

## What changed: the silent ones first

A breaking change that raises an error is easy to find. One that returns a different answer is not, and 2.0.0 has five of them. I verified each one on both versions:

| Expression | DuckDB 1.5.6 | DuckDB 2.0.0 |
| :--- | :--- | :--- |
| `SELECT 'abc' ~ 'b'` | `false` | `true` |
| `SELECT 2 * 3!` | `720` | `12` |
| `SELECT typeof(X'6162')` | `VARCHAR` | `BLOB` |
| `SELECT typeof(B'1010')` | `VARCHAR` | `BIT` |
| `CREATE TABLE t AS SELECT NULL AS x`, then column type | `INTEGER` | `"NULL"` |
| `SELECT 1 // 0` | `NULL` | error |
| `SELECT 1 % 0` | `NULL` | error |

The `~` and `!~` operators now do partial regular expression matching, following PostgreSQL: `'abc' ~ 'b'` is true because `b` occurs inside `abc`. On 1.5.6 the same expression required a full match. Any query that uses `~` to test a whole value now matches more rows, silently. The bridge, `SET regex_match_operator_semantics = 'full'`, restores `false` on 2.0.0; I verified it.

The factorial operator `!` now binds more tightly: `2 * 3!` is `2 * (3!)` = 12 on 2.0.0, where 1.5.6 read it as `(2 * 3)!` = 720. Parentheses restore the old answer on both; I measured `(2 * 3)!` = 720 on each.

The `X'...'` and `B'...'` literals now produce `BLOB` and `BITSTRING` values instead of `VARCHAR` strings. The engine reports the bit literal's type as `BIT`. A column built from those literals, or a comparison against a `VARCHAR`, now behaves differently, and a `WHERE` clause that used to match a string may stop matching.

An untyped `NULL` now keeps the `NULL` type instead of defaulting to `INTEGER`. `CREATE TABLE t AS SELECT NULL AS x` makes a `"NULL"` column on 2.0.0, and inserting a non-`NULL` value fails with a conversion error; on 1.5.6 it makes an `INTEGER` column and the insert succeeds. Cast the `NULL` to the intended type, `NULL::VARCHAR AS x`, or set `legacy_disable_null_type = true`; I verified the bridge restores `INTEGER`.

![A before-and-after table of the silent changes, with the 1.5.6 value and the 2.0.0 value side by side.](silent-changes.svg "Five expressions change their answer on 2.0.0 without raising an error; two more now raise instead of returning NULL."){: .figure}

## What changed: the loud ones

The rest of the breaking changes raise errors, which is the kind kind. Integer division and modulo by zero, `1 // 0` and `1 % 0`, now throw instead of returning `NULL`; regular division still returns infinity. Wrap one expression in `TRY(1 // 0)` to get `NULL` back for it, or set `error_on_division_by_zero = false` for the session; I verified both on 2.0.0.

Any error inside an explicit transaction now aborts the transaction. On 1.5.6, a parser or binder error, such as selecting from a missing table, left the transaction usable, so later statements could still run and commit. On 2.0.0 the `INSERT` after the failed `SELECT` raises a transaction error and the transaction has to be rolled back. I measured both: the insert commits on 1.5.6 and raises `TransactionException` on 2.0.0. The bridge is `SET default_transaction_invalidation_policy = 'SYNTACTIC_ERRORS_DO_NOT_INVALIDATE'`, which I verified restores the commit. Code that runs a may-fail statement inside a transaction needs to check first or run it outside the transaction. This is the same posture PostgreSQL has always taken, and the [transactional outbox](/posts/transactional-outbox-reliable-events-without-dual-writes/) guide on this blog assumes it.

Single-arrow lambdas are disabled by default. `list_transform([1, 2, 3], x -> x + 1)` works on 1.5.6 and raises a binder error on 2.0.0; the Python-style form `lambda x : x + 1` works on both. `SET lambda_syntax = 'enable_single_arrow'` restores the old syntax for the session, which I verified, but the bridge is temporary: DuckDB 2.1 removes the single-arrow syntax entirely, so rewrite the queries instead.

A `MERGE INTO` that would update or delete the same target row more than once now throws instead of silently using one of the source rows. I measured it: the merge completes silently on 1.5.6 and raises on 2.0.0. Deduplicate the source rows or make `ON` unique.

Around those, the parser changed to a PEG-based one, designed to be compatible (the `legacy_parser` extension is the escape hatch). ICU left the core build, so time zones, calendars, and collations now come from the native `icu` extension. `preserve_identifier_case` became a string setting; the old values still map to `'preserve_case'` and `'lowercase'`. Passing S3 settings as URL parameters is disabled by default; use secrets instead. `custom_profiling_settings` was removed in favor of `tracked_metrics`.

## What changed: the Python client

The Python client requires Python 3.11 or newer; on 3.10, `pip install duckdb` installs a 1.x release. I measured each API change below:

- `con.execute(query).fetch_arrow_table()`, `fetch_record_batch()`, `arrow()`, and `pl()` are gone from `execute()` results on 2.0.0: calling any of them raises `AttributeError`. On 1.5.6 all four exist. Use a relation instead: `con.sql(query).to_arrow_table()`. I could not run the Arrow replacement in this VM: on 2.0.0 the Arrow output calls crash the interpreter with a bus error, while the same calls work on 1.5.6. Treat the replacement form as documented but unmeasured here.
- `rel.fetchone()`, `rel.fetchmany(n)`, `rel.execute()`, and `rel.fetch_df_chunk()` are gone from relations on 2.0.0. A relation keeps no result between calls and runs its query again on every read. To keep a `fetchone()` loop, create the result with `con.execute(query)`; to iterate a relation, use `rel.iter_rows()`, which works on 2.0.0 and raises `AttributeError` on 1.5.6.
- A plain string in an expression is now a value, not a column name: write `col("x")` for the column and `lit("x")` for the text. A dotted name is never split at a dot, so `"t.x"` is one column name; write `col("t", "x")`.
- A relation attribute is now a method when a new relation method shares the name: `rel["offset"]` returns the column on both versions, while `rel.offset` is the column on 1.5.6 and the method on 2.0.0.
- `con.sql("CREATE TABLE ...")` returns `None` on 1.5.6 and a relation on 2.0.0. Use `con.execute()` for DDL and DML; printing a relation runs its query every time.
- Open `execute()` results are now guarded: running another query while one is unfinished raises `ResourceInUseException` on 2.0.0. The guard applies to queries that actually run: fetching from a relation, or writing a file, raises while the result is unfinished, while merely building a relation with `con.sql()` does not. Reading the result to its end, or calling `con.complete()`, frees the connection; a second `execute()` replaces the open result. On 1.5.6 none of this blocks, and `con.complete()` does not exist. Fetching a single row does not free the connection, only reading to the end does.
- One connection across threads now raises: two threads executing a heavy query on one connection serialize on 1.5.6 and raise `ResourceInUseException` on 2.0.0. Give each thread its own `con.cursor()`.
- `rel.write_csv(path, overwrite=False)` and `rel.write_parquet(path, overwrite=False)` replaced an existing file on 1.5.6 and raise an `IOException` on 2.0.0. Leave `overwrite` out to replace the file.
- `Decimal("1E+2")` arrives as `1.000` on 1.5.6 and `100.000` on 2.0.0. The documentation states the types as `DECIMAL(3,2)` and `DECIMAL(3,0)`; the values are what I measured.
- The Arrow output of a relation now comes in batches of 131,072 rows by default, down from 1,000,000 (documented, not measured here).

## The upgrade check

The harness shipped with this article, `duckcheck.py`, turns the measurements above into a check you run before rolling out. It runs every semantics probe against the installed engine, verifies every bridge on 2.0.0, and, given an interpreter with 1.x installed, reports whether a file opens under each version. Run it from the article folder:

```bash
python3 duckcheck.py --old-python /path/to/duckdb-1.5/python data.duckdb
```

```text
engine: duckdb 2.0.0 (2.0 line)
old interpreter: duckdb 1.5.6

semantics probes (observed -> behavior):
  regex_partial: True -> 2.0
  factorial: 12 -> 2.0
  int_div_zero: 'InvalidInputException' -> 2.0
  mod_zero: 'InvalidInputException' -> 2.0
  float_div_zero: inf -> 2.0
  hex_literal_type: 'BLOB' -> 2.0
  bit_literal_type: 'BIT' -> 2.0
  lambda_single_arrow: 'BinderException' -> 2.0
  ctas_null_type: '"NULL"' -> 2.0
  tx_after_failed_select: 'TransactionException' -> 2.0
  merge_double_match: 'InvalidInputException' -> 2.0

compatibility bridges (True = 1.x behavior restored):
  regex_full: True
  lambda_bridge: True
  div_zero_bridge: True
  try_div_zero: True
  null_type_bridge: True
  tx_bridge: True

file: data.duckdb
  new engine opens it: True ((3, Decimal('28.75')))
  old engine opens it: False (IO Error: Trying to read a database file
    with version number 69, but we can only read versions between 64 and 68.)

recommendation: this file is already on the one-way side: keep a pre-upgrade
copy and write new files with an explicit storage version while any 1.x
process remains.

recommendation: run a shadow system on 2.0.0, diff the results of your real
queries, and only then roll the fleet forward.
```

The probes are the same expressions from the tables above, so the output answers "which behavior does this engine have" rather than comparing version strings.

## The safe upgrade, step by step

For mission-critical workloads the migration guide advises considering waiting for the upcoming patch releases, and in all cases setting up a shadow system that tracks the existing workload. The steps below follow that advice.

![Six numbered steps: inventory, shadow, verify, pin the storage version, migrate, and keep the pre-upgrade copy.](upgrade-path.svg "Inventory, shadow, verify, pin the storage version, migrate, and keep the copy: the order matters because each step protects the next."){: .figure}

**1. Inventory every process and every file.** Each process that opens a DuckDB file, the version it was built against, and each file's creator version. DuckDB has no server to query for this, so the inventory is a document you maintain.

**2. Run a shadow system on 2.0.0.** A 2.0.0 process that replays the production workload against a copy of the data, outside production. Diff the results, row counts, and a checksum such as the sum of a numeric column.

**3. Verify results, not just errors.** The harness probes cover the known silent changes, but your queries may combine them in ways the probes do not. A query that returns more rows on 2.0.0 because `~` now matches partially will not raise.

**4. Pin the storage version while the fleet is mixed.** Until every process is on 2.0.0, write new files with an explicit storage version:

```python
con = duckdb.connect("data.duckdb",
                     config={"storage_compatibility_version": "v1.5.6"})
```

The same pin exists as `-storage-version` and as `STORAGE_VERSION` on `ATTACH`. I verified the Python form: a file created by 2.0.0 with the pin opens under 1.5.6 with all three rows intact. Treat the pin as temporary.

**5. Migrate the file deliberately.** To move a file to v69, export it with the older version, then import it with 2.0.0:

```bash
duckdb-1.5 data.old.db -c "EXPORT DATABASE 'tmp'"
duckdb-2.0 data.new.db -c "IMPORT DATABASE 'tmp'"
```

I verified the round trip: `EXPORT DATABASE` under 1.5.6 and `IMPORT DATABASE` under 2.0.0 preserved all three rows and the sum of 28.75. `COPY FROM DATABASE` is the other documented route.

**6. Keep the pre-upgrade copy.** The copy is the rollback: no downgrade command, no flag that turns a v69 file back into a v68 file, and no `ATTACH` option that makes 1.5.6 read v69. The copy, plus the export directory from step 5, is the entire rollback plan.

The shadow is also where you evaluate the new features. Quack turns a DuckDB instance into a server: `CALL quack_serve()` listens on localhost by default on port 9494, and `ATTACH 'quack:localhost' AS qk` followed by `CONNECT qk` routes a session to it. For anything beyond localhost, the documentation recommends a TLS-terminating reverse proxy; `allow_other_hostname` is only meant for testing. I could not measure Quack in this VM: installing the extension fails because DuckDB's HTTP client cannot parse the sandbox egress proxy URL, and without the proxy there is no network. If shared files are your problem, Quack is the architectural answer, but verify it on your own network first.

## Failure modes

| What you see | Cause | Fix |
| :--- | :--- | :--- |
| Old processes fail at open with "version number 69, but we can only read versions between 64 and 68" | One 2.0.0 process created a file, or a file was migrated to v69, while 1.x processes still share it | Restore the pre-upgrade copy; pin `storage_compatibility_version = 'v1.5.6'` until the fleet is uniform |
| A report returns more rows, or different rows, with no error | `~` now matches partially, `!` binds tighter, or a literal changed type | Diff shadow results against production; use `regex_match_operator_semantics = 'full'` only as a bridge while you fix the patterns |
| A pipeline fails at import or at the first Arrow call | `fetch_arrow_table` and friends are gone from `execute()` results; `rel.fetchone` and `rel.fetchmany` are gone from relations | Use `con.sql(query).to_arrow_table()` and `rel.iter_rows()`; run the pipeline against 2.0.0 before deploying it |
| A job that ran a may-fail statement inside a transaction now aborts the whole transaction | Any error inside an explicit transaction aborts it on 2.0.0 | Check first or run the statement outside the transaction |
| A long-running job dies with `ResourceInUseException` | Two threads share one connection, or a second query runs while an `execute()` result is unfinished | One `con.cursor()` per thread; read results to the end or call `con.complete()` before the next query |

The first row costs the most: it is discovered by the processes you did not upgrade, at the moment they try to open the file, and the fix is a restore rather than a setting.

## Proving it works

The suite shipped with this article, `test_duckcheck.py`, has 16 tests, all passing on duckdb 2.0.0 with deprecation warnings as errors:

```bash
python3 -m pytest test_duckcheck.py -W error::DeprecationWarning
```

The suite runs the semantics probes against the installed engine and asserts the values for that line, verifies every bridge restores the 1.x behavior, checks the Python API removals and replacements, and, when `DUCKDB_OLD_PYTHON` points at a 1.x interpreter, runs the four cross-version file tests: a new file is unreadable by the old version, a pinned file is readable, an old file written by the new engine stays readable, and the export/import round trip preserves the rows and the sum. The same suite passes on 1.5.6 with 10 passing and 6 skipped.

## Operating it

After the upgrade, the file inventory from step 1 becomes a standing record: file path, creator version, storage version as recorded at creation, and the date the pre-upgrade copy expires. No SQL query reports a file's storage version, so the record is maintained by the process that creates the file, and `duckcheck.py` is the check that the record is true.

Watch for the IO Error at open time in your process logs; it is the signal that a file crossed the door while a 1.x process still needed it. Watch the shadow diff as a standing job, not a one-off: run the same queries on both versions for a full error-budget window and alert on any row-count or checksum difference, the way you would alert on any [error budget](/posts/slos-and-error-budgets-for-one-service/) burn. Run DuckDB 2.0.0; plan for 2.0.1, due 2026-11-20.

## Trade-offs and alternatives

Waiting is a legitimate choice. DuckDB 1.5 is supported until March 2027, so a team that needs more time can stay on 1.5.6 while the shadow runs and upgrade to 2.0.1 or later instead of 2.0.0. The cost of waiting is small: 2.0.0 is an LTS release supported until at least October 2027, and the patch release due 2026-11-20 addresses the issues that surfaced shortly after the major release.

Staying on 1.5 forever is not a choice: 1.4 reached end of life on 2026-11-17, and 1.5 follows in March 2027. The upgrade is a when, not an if.

Pinning the storage version indefinitely is a trap. It keeps files readable by 1.x, which is useful for exactly one migration window, but it hides the version skew instead of resolving it. Pin during the migration and remove the pin when the last 1.x process is gone.

Quack is the alternative to shared files entirely: serving data over Quack instead of passing a file around removes the storage-format question from the deployment, because the server owns the file and the clients only speak the protocol. That is a bigger change than an upgrade, and it needs its own evaluation, including the reverse-proxy setup. Do not adopt it as part of the 2.0 upgrade.

## Checklist

- [ ] Inventory every process and file version before touching anything.
- [ ] Run a shadow system on 2.0.0 and diff real query results.
- [ ] Run `duckcheck.py` against every shared file with both interpreters.
- [ ] Pin `storage_compatibility_version = 'v1.5.6'` while any 1.x process remains.
- [ ] Keep a pre-upgrade copy of every file, plus the export directory.
- [ ] Rewrite single-arrow lambdas and `rel.fetchone` loops instead of leaning on the bridges.
- [ ] Check 2.0.1 the same way when it lands: harness, shadow diff, rollout.
- [ ] Remove the storage-version pin once the last 1.x process is gone.

## References

- DuckDB, [Migrating to DuckDB 2.0](https://duckdb.org/docs/2.0/operations_manual/migration), 2026. Storage format v69, the silent and loud changes, the bridges, and the shadow-system advice.
- DuckDB, [Migrating Python Code to DuckDB 2.0](https://duckdb.org/docs/2.0/clients/python/migration), 2026. Every Python API change in this article.
- DuckDB, [Announcing DuckDB 2.0.0 LTS "Cinnamon Teal"](https://duckdb.org/2026/10/21/announcing-duckdb-200), 2026-10-21. The release, the LTS support window, and the Quack, VARIANT, trigger, and parser changes.
- DuckDB, [Quack Remote Protocol](https://duckdb.org/docs/2.0/quack/overview), 2026. `quack_serve` on localhost by default, port 9494, and the reverse-proxy recommendation.
- DuckDB, [Release Calendar](https://duckdb.org/release_calendar), 2026. 2.0.1 due 2026-11-20 (tentative), 1.4 LTS end of life 2026-11-17, 1.5 support to March 2027.
