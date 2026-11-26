---
title: "Valkey 9.2 Forkless Snapshots: BGSAVE Without fork()"
description: >-
  Valkey 9.2 replaces the fork() behind BGSAVE with a background thread.
  Measured on a real 9.2.1 build: peak memory during a save falls from
  +52.7 MB to +1.1 MB, and writes pay about 2.4 ms at p99.
date: 2026-11-26 15:35:00 +0000
author: ritesh
categories: [Database, Reliability]
tags: [valkey, redis, persistence, memory, backup]
kind: Deep Dive
draft: false
cover:
  image: cover.webp
  alt: "Two bars comparing peak memory during BGSAVE: fork reaches 193.2 MB, forkless reaches 141.5 MB, against a 140.4 MB baseline."
---

Every Valkey snapshot since the Redis days has been paid for with `fork()`. When `BGSAVE` runs, the server forks, the child writes the RDB file, and the parent keeps serving. The trick that makes it safe is copy-on-write: parent and child share every page until one of them writes to it, and then the kernel copies that page. Under write load, the parent dirties pages while the child is still reading them, and each dirtied page is copied. The server's memory grows by exactly the pages its own writes touched: a snapshot that succeeds on a quiet server and OOM-kills a busy one.

Valkey 9.2.0, released 2026-11-18 with a 9.2.1 follow-up on 2026-11-25, removes the fork from the snapshot path: `BGSAVE` and replica full syncs can run on a background thread inside the same process. No child, no page table copy, no copy-on-write spike. The cost moves elsewhere: 4 bytes of metadata per key, and writes to keys the thread has not reached yet must wait.

This article targets **Valkey 9.2.1 and Python 3.12**. Every number below was measured on a Valkey 9.2.1 server built from the release source in this run, with the probe harness shipped next to the article (`forkless_probe.py`, standard library only). Run 9.2.1, not 9.2.0: it fixes a crash when `PHGET` reads a large path hash during a forkless save, restores pre-9.2 TLS certificate loading, and fixes a dual-channel replication resync bug.

> [!NOTE]
> **In short**
> - A fork `BGSAVE` costs almost nothing in memory on a quiet server and spikes under write load: +52.7 MB peak on a 140.4 MB dataset here, with a 34 to 49 ms stall for writes while the fork runs.
> - Valkey 9.2 adds forkless snapshots: a background thread serializes the keyspace while the main thread keeps serving. Measured peak extra memory: +1.1 MB.
> - Turn it on with two config lines, set before the server starts: `forkless-infrastructure-enabled yes` (startup only, 4 bytes of metadata per key) and `forkless-policy prefer-forkless`.
> - The trade is latency, not memory: writes during a forkless save wait for keys the thread has not reached yet. Measured p99 write latency 2.4 ms during the save, against 0.09 ms with fork.
> - AOF rewrites still fork, and `prefer-forkless` silently falls back to fork for modules, slot imports, and data-excluding RDB requests. Watch `rdb_last_bgsave_type`; do not assume.
> - Valkey 9.2 writes RDB version 81. A 9.1 server refuses it under the default strict check, so the upgrade is one way until every process is on 9.2.

## How a fork snapshot spends memory

The persistence docs state the deal plainly: the only work the parent does to persist is forking a child, and the parent never performs disk I/O. They also warn that `fork()` can be time consuming if the dataset is big, and may stop the server serving clients for some milliseconds, or even for one second if the dataset is very big. That stall is the page table copy, which runs on the main thread, with no client served until it finishes.

The memory spike is a second, separate cost. After the fork, parent and child share every page. The child reads the pages to write the RDB file, and every parent write to a shared page forces the kernel to copy that page first, so the parent keeps its own copy and the child keeps the old one. The spike is proportional to the pages dirtied during the save, not to the dataset size. A quiet server pays almost nothing; a busy server can pay up to the whole dataset, while the save is running.

![The classic fork BGSAVE: parent and child share pages, a write forces a copy, and parent RSS grows.](fork-bgsave.svg "The fork BGSAVE: a write to a shared page forces a copy-on-write, and parent RSS grows."){: .figure}

Two details make the spike worse than the page count suggests. First, transparent hugepages: this run's host had them set to `madvise`, and Valkey's default `disable-thp yes` asks the kernel to switch them off for the server process. The numbers here fit 4 KiB pages: 12,000 to 16,000 writes per save, 49 to 57 MB. On a host set to `always`, a touched 2 MB hugepage copies whole, and the spike would be far larger. Second, the fork can fail outright: with the default heuristic overcommit setting, a fork of a large process under memory pressure can be refused. The server logs the usual warning at startup: memory overcommit must be enabled, or a background save or replication may fail under low memory conditions.

That is the cost model for the rest of the article: a fork snapshot trades memory headroom and one stall for a simple mechanism, and forkless trades a little latency during the save for removing both.

## How forkless works

A forkless save replaces the child process with a background thread and an iterator. The thread walks the keyspace in order and serializes each key into the RDB file while the main thread keeps serving. There is no second address space, so there is nothing to copy on write. The snapshot still has to be a point-in-time image, so the writers pay instead of the memory.

Each key carries 4 bytes of metadata when the infrastructure is enabled: a 32-bit iterator epoch recording the last modification. That is the field the configuration documents as costing 4 additional bytes per key. When a write arrives, the main thread checks the keys it touches against the iterator:

- If the key is a string whose key plus value is 512 bytes or less, Valkey clones the old version into a pool capped at 1 MB total, and the write proceeds at once.
- If the key is larger, or it is a hash, list, set, or sorted set, it cannot be cloned. The main thread expedites the key to the front of the background thread's work, and the client blocks until the thread has serialized the old version.
- Reads never block. Only writes to keys the iterator has not reached yet can wait.

![The forkless BGSAVE: a background thread serializes keys while the main thread serves, cloning small strings and blocking writes to larger keys.](forkless-bgsave.svg "The forkless BGSAVE: small strings are cloned from a 1 MB pool, larger values wait for the iterator."){: .figure}

Three scope notes matter. First, in 9.2 forkless applies to RDB snapshots and full replica syncs, disk-based and diskless; AOF rewrites still use `fork()`. Second, `prefer-forkless` falls back to fork when an operation cannot run forkless: a loaded module has not set the forkless flag, a slot import is in progress, or a data-excluding RDB request. The server counts these fallbacks, so they are observable, but the save still happens, just by fork. Third, enabling the infrastructure alone changes nothing: it only adds the metadata, and the policy setting is what turns forkless on.

## Turning it on

Two lines in the server configuration file, before the server starts:

```text
forkless-infrastructure-enabled yes
forkless-policy prefer-forkless
```

The first line is immutable and must be set at startup, because it changes the per-key allocation. `CONFIG SET forkless-policy prefer-forkless` on a server that started without it is refused, and the policy stays at `require-fork`. The second line accepts `CONFIG SET` at runtime: start with the infrastructure enabled, baseline with fork, then flip the policy and compare on the same server. The 9.2.1 defaults are `forkless-infrastructure-enabled no` and `forkless-policy require-fork`, so an upgrade alone changes no behaviour.

Verify it with `INFO persistence`: a forkless save reports `rdb_last_bgsave_type:forkless`, and while one runs, `rdb_current_bgsave_type` reports `forkless` and `forkless_estimated_seconds_remaining` gives an ETA. If a save reports `fork` while the policy is `prefer-forkless`, check the `stat_forkless_fallbacks_*` counters in `INFO`.

## Measuring it: memory

The shipped `forkless_probe.py` starts a real 9.2.1 server, loads a dataset, runs `BGSAVE` under a write load, and samples the server process group's memory from `/proc` every 25 ms. The metric is the sum of proportional set size (Pss) over the server and its fork child, which counts shared pages once. The dataset is 100,000 keys of 1 KiB values, a baseline group Pss of about 140.4 MB, and a single writer thread issuing random `SET`s for the whole save, three runs per mode. Host settings: transparent hugepages `madvise`, overcommit heuristic (`vm.overcommit_memory=0`), 4 CPUs.

| Run | Fork peak extra | Fork save time | Forkless peak extra | Forkless save time |
| --- | --- | --- | --- | --- |
| 1 | 49.4 MB | 0.71 s | 1.1 MB | 0.65 s |
| 2 | 51.6 MB | 0.71 s | 1.0 MB | 0.70 s |
| 3 | 57.2 MB | 0.73 s | 1.2 MB | 0.64 s |
| Mean | **52.7 MB** | 0.72 s | **1.1 MB** | 0.66 s |

The fork spike is 38 percent of the baseline dataset size, and it is not noise: the three runs agree within 8 MB. Save time is essentially the same in both modes, 0.66 s against 0.72 s: the background thread serializes about as fast as the child did.

![Peak extra memory during BGSAVE, fork against forkless, mean of three runs each.](peak-rss.svg "Peak extra memory during BGSAVE: fork adds 52.7 MB, forkless adds 1.1 MB."){: .figure}

Scale the result to a real dataset before deciding it does not matter. The spike grows with the pages dirtied during the save, which grows with the write rate and the save duration. On this run the writer sustained about 20,000 operations per second during a 0.72 s fork save. A 10 GB dataset with the same write rate and a 30 s save would need headroom measured in gigabytes, at the exact moment the machine is busiest. That is why the folk rule for Valkey and Redis has been to size `maxmemory` at about half of RAM. Forkless removes the term: the peak is the dataset plus the 1 MB clone pool, whatever the write rate.

## Measuring it: latency

A second experiment used 50,000 keys of 1 KiB plus 100 keys of 256 KiB, so the writer issued both small and large `SET`s during the save, three runs each:

| Mode | Small SET p99 | Small SET max | Large SET p99 | Large SET max |
| --- | --- | --- | --- | --- |
| Fork | 0.089 ms | 33.7 to 48.5 ms | 0.79 ms | 0.99 to 1.47 ms |
| Forkless | 2.33 ms | 2.8 to 4.3 ms | 2.35 ms | 2.7 to 3.3 ms |

Two things stand out. First, the fork runs have a tail the forkless runs do not: every fork save produced a 34 to 49 ms stall, the `fork()` page table copy on a 140 MB process, and the persistence docs warn it can reach a second on a very large dataset. Second, the forkless runs have a raised p99 instead: 2.33 ms against 0.089 ms. That is the expedite-and-block path. Small and large values show almost the same p99, about 2.3 ms, consistent with the background thread's cycle: a write waits roughly one iteration cycle for the thread to serialize its key, and the wait does not grow with the value size at this scale.

A control run with no save in progress shows both modes identical: about 36,000 operations per second from one writer thread, p99 0.065 ms. The forkless p99 is caused by the save, not by the infrastructure; the median is unaffected, p50 0.024 ms everywhere. During a save, the single writer completed about 20,000 operations per second in fork mode and about 12,000 in forkless mode, so the throughput cost is real too. One forkless run in the memory experiment showed a single 38.6 ms write; it did not repeat in the latency runs, and I have no explanation for it.

The 4 bytes per key also measures differently from the documentation. Loading 200,000 small keys with the infrastructure off and on, `used_memory` differs by 8.0 bytes per key; at 500,000 keys it is 7.99. The metadata field is 4 bytes, but jemalloc rounds the entry allocation up one size class, so the resident cost on this build is 8 bytes per key: 8 MB for a million keys, not 4 MB. Still negligible next to the data, but quote the measured number, not the documented one.

## The three production mistakes

**1. Treating forkless as a runtime toggle.** The infrastructure flag is immutable at startup, and enabling it alone changes nothing. The failure looks like this: an operator enables the infrastructure, runs `BGSAVE`, checks `rdb_last_bgsave_type`, sees `fork`, and concludes forkless is broken. It is not broken; the policy is still `require-fork`. Worse, an operator who tries `CONFIG SET forkless-policy prefer-forkless` on a server that started without the infrastructure gets an error and may conclude the feature is unavailable on 9.2. Plan the restart with the 9.2 upgrade, not after it; the shipped test `test_policy_refused_without_infrastructure` proves the refusal.

**2. Sizing memory for the steady state, not the save.** The fork spike is invisible in steady-state monitoring: `used_memory` is flat, the dashboards are green, and then the hourly `BGSAVE` fires during peak traffic and the OOM killer takes the server. If you stay on fork, size for the spike, not the dataset: measure it with the shipped harness under your real write rate and keep that much headroom. If you switch to forkless, the failure mode flips to latency: a service with a tight p99 budget and mostly large values will breach its budget during every save, because those writes wait for the iterator. Measure the p99 during a save before enabling it in production, and compare it against your error budget, not against the fork spike. See [SLOs and Error Budgets for One Service](/posts/slos-and-error-budgets-for-one-service/) for how to turn that comparison into a number.

**3. Assuming every save goes forkless.** `prefer-forkless` is a preference, not a guarantee. A module that has not set the forkless flag, a slot import in progress, or a data-excluding RDB request all fall back to fork, silently, and the save still succeeds. An operator who enables forkless and stops watching memory will miss the one save a week that forks and spikes. AOF rewrites always fork in 9.2, so a deployment that rewrites its AOF every hour still pays the fork cost on that path. Monitor `rdb_last_bgsave_type` after every save and alert when it reports `fork` while the policy is `prefer-forkless`.

Two more traps belong here. The first is the version: 9.2.0 shipped with a forkless-save crash, fixed in 9.2.1 when `PHGET` reads a large path hash during a save. Run 9.2.1. The second is the downgrade: 9.2 writes RDB version 81, and the 9.1 source refuses any RDB version above its own 80 under the default strict `rdb-version-check`. A 9.2 snapshot cannot be loaded by 9.1, and the release blog warns to switch `rdbcompression` back to a legacy mode and run `BGREWRITEAOF` before downgrading, because AOF bases written with `lz4` or `zstd` also require 9.2. Keep a pre-upgrade copy and a tested rollback that does not depend on loading a 9.2 file with a 9.1 binary.

## Proving it works

The shipped `test_forkless.py` runs 11 tests against a real 9.2.1 build, all passing on Python 3.12.3 with pytest 9.2.0:

- A forkless `BGSAVE` reports `rdb_last_bgsave_type: forkless` with status `ok`, and a fork `BGSAVE` reports `fork`.
- `CONFIG SET forkless-policy prefer-forkless` is refused on a server started without the infrastructure, and the policy stays `require-fork`.
- A forkless snapshot round-trips: after `BGSAVE`, a restart from the RDB file finds all 500 keys intact.
- The memory property: on the same dataset and write load, the forkless save's peak extra memory is less than half the fork save's.
- Large-value writes during a forkless save stay bounded: p99 under 10 ms at 20,000 keys.
- The infrastructure overhead per key measures between 4 and 16 bytes (measured 8.0).
- Four pure-logic tests cover RESP parsing, `INFO` parsing, and latency statistics.

Run them with `VALKEY_SERVER=/path/to/valkey-server python3 -m pytest test_forkless.py -v`; the server tests skip with a clear message when no binary is available. Build the server from the 9.2.1 source with `make`.

## Operating it

Watch `INFO persistence` and `INFO stats`. After every save, check `rdb_last_bgsave_type` and `rdb_last_bgsave_status`. While a save runs, `rdb_bgsave_in_progress` is 1 in both modes, so existing monitoring keeps working, and `forkless_estimated_seconds_remaining` gives an ETA for forkless saves. Track `rdb_last_cow_size` and `current_cow_peak` for fork saves and the `stat_forkless_fallbacks_*` counters for forkless ones. Alert when a save reports `fork` while the policy is `prefer-forkless`, when a forkless save's duration grows week over week, or when write p99 during save windows rises above the latency budget the service promised.

Schedule saves deliberately. The default save points (3600 seconds with 1 change, 300 with 100, 60 with 10,000) fire on write count, which means they fire during traffic. If the service is latency sensitive, keep the automatic points for safety and add an explicit off-peak `BGSAVE`, so the bulk of saves happen when the write rate, and therefore the forkless wait queue, is small. If the instance is only a cache, disable saves with `save ""` and skip this whole problem; the right defence for a cache is different, and [Stopping Cache Stampedes: Three Defenses Compared](/posts/cache-stampede-defenses-compared/) covers it.

## Trade-offs and alternatives

Forkless is not free. It costs 4 bytes of metadata per key, 8 bytes of resident memory per key on jemalloc, and write latency during saves: p99 2.4 ms here, against 0.09 ms with fork. The wait for one write is bounded by the time the background thread needs to serialize that key: short for one key, but it can approach the remaining save time if the key is last in iteration order and the dataset is large. A service whose p99 budget is under a millisecond during saves should not enable it blindly.

When not to use it: values are mostly large and the latency budget is tight; a required module has not set the forkless flag, so every save would fall back to fork anyway; or the fleet cannot all move to 9.2, so the RDB version 81 files would strand the 9.1 processes. In the last case, wait until the whole fleet is on 9.2.

The alternatives, with the condition under which each wins:

- **Stay on fork and size for the spike.** Wins when the latency budget is tight and memory is cheap. Measure the spike under real write load with the shipped harness, keep that much headroom, and set `vm.overcommit_memory=1` so the fork cannot be refused under pressure.
- **Run backups from a replica.** Wins when the primary's latency matters more than anything else. The fork, and its spike and stall, happen on the replica. The cost is a replica and the replication lag at backup time.
- **AOF only, no RDB.** Wins when every write must be durable and restarts are rare. There is no `BGSAVE` at all, so there is no spike and no forkless question. The cost is slower restarts and no compact point-in-time file. An RDB snapshot is a point-in-time image, not a log: if the application needs every write accounted for, the durability argument belongs with the write path, as in [Transactional Outbox: Reliable Events Without Dual Writes](/posts/transactional-outbox-reliable-events-without-dual-writes/), not with the snapshot schedule.
- **Forkless for RDB, AOF rewrite off-peak.** Wins for most 9.2 deployments: snapshots stop spiking, and the remaining fork, the AOF rewrite, runs when the write rate is low.

My recommendation: enable forkless for RDB snapshots on 9.2.1 when your values are mostly small or your latency budget tolerates a few milliseconds at p99 during saves, and measure both numbers first with the shipped harness. Keep watching `rdb_last_bgsave_type`.

## Checklist

- [ ] Upgrade to 9.2.1, not 9.2.0, on every process before enabling forkless.
- [ ] Set `forkless-infrastructure-enabled yes` and restart; confirm `CONFIG GET forkless-policy` accepts `prefer-forkless`.
- [ ] Run one `BGSAVE` and confirm `INFO persistence` reports `rdb_last_bgsave_type: forkless`.
- [ ] Measure your own spike and p99 with the shipped harness under your real write rate.
- [ ] Alert when a save reports `fork` while the policy is `prefer-forkless`.
- [ ] Keep a pre-upgrade copy; do not plan a rollback that loads a 9.2 RDB file with a 9.1 binary.
- [ ] Remember AOF rewrites still fork; schedule them off-peak.
- [ ] Re-check the numbers after any version change: a patch release can move the behaviour, as 9.2.1 did for the `PHGET` crash.

## References

- Valkey, [Valkey 9.2 offers forkless snapshots, compressed replication, ACL roles, and more](https://valkey.io/blog/valkey-9.2-release/)
- Valkey, [Valkey 9.2.0 GA release notes](https://github.com/valkey-io/valkey/releases/tag/9.2.0)
- Valkey, [Valkey 9.2.1 release notes](https://github.com/valkey-io/valkey/releases/tag/9.2.1)
- Valkey, [valkey.conf at 9.2.1](https://raw.githubusercontent.com/valkey-io/valkey/9.2.1/valkey.conf)
- Valkey, [Persistence](https://valkey.io/topics/persistence/)
- Valkey, [bgiteration.c at 9.2.1](https://raw.githubusercontent.com/valkey-io/valkey/9.2.1/src/bgiteration.c)
- Linux, [fork(2) man page](https://man7.org/linux/man-pages/man2/fork.2.html)
