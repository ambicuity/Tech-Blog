---
title: "Stopping Cache Stampedes: Three Defenses Compared"
description: >-
  One hot key expires and 32 requests hit the origin at once. TTL jitter,
  single-flight coalescing, and stale-while-revalidate compared on one
  harness, with measured loader counts.
date: 2026-10-13 14:00:00 +0000
author: ritesh
categories: [Performance, Reliability]
tags: [caching, cache-stampede, redis, valkey, python, single-flight, stale-while-revalidate]
kind: Comparison
draft: false
cover:
  image: cover.webp
  alt: Thirty-two requests flow into a cache holding three defenses, TTL jitter, single-flight, and stale-while-revalidate, and one load reaches the origin.
---

Consider a product page cached with a one-hour TTL. The entry is written at 11:00, so it expires at 12:00:00. At 12:00:00, thirty-two requests for that page arrive in the same second. Every one of them misses. Every one of them runs the same database query, the same downstream call, the same render. The cache that was supposed to protect the origin has just synchronized an attack on it.

This is a cache stampede, also called a thundering herd or a dogpile. It needs three ingredients: a popular key, a shared expiry, and a load expensive enough to matter. All three are normal. The fix is not to remove the TTL. The fix is to break one of the three ingredients, and there are exactly three standard ways to do it: spread the expiry, coalesce the loads, or keep serving the old value while one refresh runs.

This article compares those three defenses on one harness, with measured numbers, and ends with a recommendation. It targets Python 3.12 (standard library only for the cache itself), Redis 8.10.2, and Valkey 9.1.2. Both cache releases are current security releases: run them. Neither changed stampede technique; the comparison below is durable, and the pins are there so the Redis mapping matches what you install today.

> [!NOTE]
> In short:
> - TTL jitter spreads expiry so keys do not all die together. It is the cheapest defense and it never blocks a caller.
> - Single-flight coalescing turns 32 concurrent loads of one key into 1 load. Waiters block for the full load time, and a hung loader wedges them unless the wait has a timeout.
> - Stale-while-revalidate serves the old value while one background refresh runs. Callers never wait, but they see stale data for up to the grace window.
> - Default stack: all three together. Single-flight alone when freshness is contractual. Jitter alone as the five-minute first step.

## The stampede, precisely

Cache-aside is the usual pattern: check the cache, on a miss load from the origin, store the result with a TTL, return it. The failure is in the word "on a miss". When N requests miss the same key at the same time, the code runs N loads, because nothing coordinates the miss. The requests do not know about each other, and the cache does not remember that a load is already in flight.

![Thirty-two requests miss the same expired entry and each one loads from the origin.](stampede.svg "One expiry synchronizes thirty-two identical loads."){: .figure}

The damage scales with the cost of the load and the number of waiters. A 300 ms load with 32 waiters is 32 loads' worth of work on the origin in one instant, and the slowest waiter still waits 300 ms. Worse, the stampede can cascade: the origin slows under the burst, the next key's load takes longer, more waiters pile onto it, and the burst becomes an outage. The defenses below all work by making the miss coordinated instead of independent.

## Defense 1: TTL jitter

Jitter breaks the "shared expiry" ingredient. Instead of writing every entry with the same TTL, write each one with a TTL drawn from a band around the target: `base * (1 +/- spread)`. Keys written together then expire at different times, and the misses arrive as a trickle instead of a spike.

```python
def jittered_ttl(base_ttl: float, spread: float, rng: random.Random) -> float:
    """Return a TTL drawn from ``base_ttl * (1 +/- spread)``.

    Apply this at write time, once per key, so keys written together do not
    expire together. ``spread`` is a fraction: 0.1 on a 3600s TTL spreads
    expiry across 3240s..3960s. The 1s floor keeps a pathological
    ``base_ttl`` or ``spread`` from producing a zero or negative TTL.
    """
    if base_ttl <= 0:
        raise ValueError(f"base_ttl must be positive, got {base_ttl}")
    if not 0.0 <= spread < 1.0:
        raise ValueError(f"spread must be in [0, 1), got {spread}")
    return max(base_ttl * (1.0 + rng.uniform(-spread, spread)), 1.0)
```

Two details matter. First, apply jitter at write time, once per key. Jittering at read time, or re-randomizing on every access, does not spread expiry; it just makes expiry unpredictable. Second, `spread` is a fraction of the TTL, not an absolute number. AWS's caching guide suggests the same idea with `ttl = 3600 + (rand() * 120)`; the symmetric form above keeps the average TTL at the target instead of drifting it upward.

![Eight keys with identical TTLs expire at once; with jitter their expiry spreads across 720 seconds.](jitter.svg "Jitter turns one synchronized expiry into a trickle of misses."){: .figure}

Measured on 200 keys with TTL 3600 s and spread 0.1: expiry landed between 3246 s and 3960 s, a spread of 714 s, instead of all 200 expiring at 3600 s. Jitter's weakness is that it only decorrelates expiry. It does nothing for the stampede that happens anyway: a cold cache, a newly added cache node with empty memory, or a key that a hundred requests hit in the same second for the first time. For those, you need coordination.

## Defense 2: single-flight coalescing

Single-flight breaks the "N loads" ingredient. When several callers miss the same key at the same time, exactly one of them becomes the leader and runs the loader. The rest wait, then share the leader's result. Go's `golang.org/x/sync/singleflight` package is the canonical version of this idea; the implementation below is the same mechanism in Python.

```python
    def _load_coalesced(self, key, loader, ttl, jitter, stale_grace, wait_timeout):
        """Run ``loader`` once per key; concurrent callers share the result.

        The first caller becomes the leader and records its outcome in a
        ``_Call``. Later callers wait on the call's event: on success they
        get the leader's value, on failure they get the leader's exception.
        Nobody loads twice for the same miss, and a failed load is not
        silently retried once per waiter. ``wait_timeout`` bounds how long
        a waiter blocks: on expiry it raises CacheTimeoutError instead of
        waiting on a hung loader forever.
        """
        with self._guard:
            call = self._calls.get(key)
            if call is None:
                call = _Call()
                self._calls[key] = call
                leader = True
            else:
                leader = False
        if not leader:
            self._stats.increment("coalesced_waits")
            finished = call.done.wait(timeout=wait_timeout)
            if not finished:
                self._stats.increment("timeouts")
                raise CacheTimeoutError(
                    f"timed out after {wait_timeout}s waiting for the load of {key!r}"
                )
            if call.error is not None:
                raise call.error
            return call.value
        try:
            self._stats.increment("loads")
            value = loader()
        except BaseException as exc:  # noqa: BLE001 - the error is shared, not swallowed
            self._stats.increment("loader_errors")
            call.error = exc
            self._entries.pop(key, None)
            raise
        else:
            call.value = value
            self._store(key, value, ttl, jitter, stale_grace)
            return value
        finally:
            call.done.set()
            with self._guard:
                if self._calls.get(key) is call:
                    del self._calls[key]
```

Three design decisions deserve attention. First, the leader records its outcome, including failure, and waiters get the same outcome. A failed load is not retried once per waiter: with 32 waiters and a dead origin, naive retry-on-failure would run 32 loads; here it runs one. Second, the wait has a timeout. Without it, a loader that hangs forever wedges every waiter forever, which is worse than the stampede. With it, a timed-out waiter gets `CacheTimeoutError` and can fall back to stale data or an error of its own choosing. Third, the in-flight record is removed in a `finally`, so a leader that crashes out of the loader never leaves a phantom call behind.

Measured on the same harness, 32 threads on one key with a 300 ms loader: 1 load, 31 coalesced waits, all 32 callers got the same value. The price is latency: every waiter blocks for the full load. Single-flight also only helps within one process. When the cache is shared across processes, the lock has to move into Redis; the [Redis lock](#redis-distributed-single-flight) section shows that mapping.

## Defense 3: stale-while-revalidate

Stale-while-revalidate (SWR) breaks the "callers wait" ingredient. An entry gets two deadlines instead of one: `fresh_until`, before which it serves as normal, and `stale_until`, until which it may still be served while a refresh runs in the background. The idea comes from RFC 5861's `stale-while-revalidate` Cache-Control extension, which lets HTTP caches serve a stale response while revalidating in the background.

```python
    def _refresh_in_background(self, key, loader, ttl, jitter, stale_grace) -> None:
        """Refresh ``key`` on a daemon thread, at most one at a time.

        On success the entry becomes fresh again. On failure the stale
        entry is left exactly as it is: it keeps serving until
        ``stale_until``, and the next caller after that loads synchronously.
        A failed refresh never extends the staleness window, so stale data
        cannot become permanent just because the loader keeps failing.
        """
        with self._guard:
            if key in self._refreshing:
                return
            self._refreshing.add(key)

        def _run() -> None:
            try:
                self._stats.increment("loads")
                value = loader()
            except BaseException:  # noqa: BLE001 - counted, then dropped: callers already got stale
                self._stats.increment("refresh_failures")
                self._stats.increment("loader_errors")
            else:
                self._store(key, value, ttl, jitter, stale_grace)
                self._stats.increment("refreshes")
            finally:
                with self._guard:
                    self._refreshing.discard(key)

        thread = threading.Thread(target=_run, name=f"cache-refresh-{key}", daemon=True)
        thread.start()
```

The entry point ties the three pieces together: fresh entries return immediately, stale entries inside the grace window return the old value and trigger a refresh, and anything past the grace window loads synchronously through single-flight.

```python
    def get(
        self,
        key: str,
        loader,
        *,
        ttl: float,
        jitter: float = 0.0,
        stale_grace: float = 0.0,
        singleflight: bool = True,
        wait_timeout: float | None = None,
    ):
        """Get ``key``, loading it if needed, with stampede defenses.

        Decision tree, in order:

        1. Fresh entry: return it.
        2. Stale entry inside ``stale_grace``: return the stale value and
           start exactly one background refresh.
        3. Otherwise: load (coalesced through single-flight unless
           ``singleflight=False``) and store with a jittered TTL.
        """
        now = self._clock.now()
        entry = self._entries.get(key)
        if entry is not None and now < entry.fresh_until:
            self._stats.increment("hits")
            return entry.value
        if entry is not None and stale_grace > 0 and now < entry.stale_until:
            self._stats.increment("stale_served")
            self._refresh_in_background(key, loader, ttl, jitter, stale_grace)
            return entry.value
        if singleflight:
            return self._load_coalesced(key, loader, ttl, jitter, stale_grace, wait_timeout)
        self._stats.increment("loads")
        value = loader()
        self._store(key, value, ttl, jitter, stale_grace)
        return value
```

![Callers past freshness get the stale value immediately while one background refresh runs; later callers get the fresh value.](swr.svg "Stale-while-revalidate trades bounded staleness for zero caller waits."){: .figure}

Measured: 32 threads arriving inside the grace window were all served the stale value, with 1 background load and 1 refresh, and zero threads blocked on the loader. The price is staleness: callers see data up to `stale_grace` old. The other price is subtler: if the loader keeps failing, the stale entry keeps serving until `stale_until`, and then the next caller blocks on a synchronous load. That is the correct behavior, a bound, not a cliff, but it means `stale_grace` is a freshness contract you are writing, not a performance knob you can set and forget.

## Side by side

All three measurements come from the same harness: 32 threads, one key, one 300 ms loader, one cache. The baseline with no defense runs 32 loads.

| Defense | Loader calls (32 threads) | Caller latency on a miss | Staleness | When the loader fails |
| :--- | :--- | :--- | :--- | :--- |
| None (baseline) | 32 | Full load, each caller | None | Each caller sees its own failure |
| TTL jitter | 32 on a synchronized miss; fewer otherwise | Full load | None | Same as baseline |
| Single-flight | 1 | Full load for every waiter | None | One shared failure |
| Stale-while-revalidate | 1 (background) | Zero for stale callers; full load past the grace window | Up to `stale_grace` | Stale served until the grace window ends, then callers see the failure |

Read the table as a decision procedure, not a ranking. Jitter is the only defense that costs nothing at read time, so it goes on every key. Single-flight is the right call when the data must be fresh and callers can wait: a price, a balance, an authorization decision. SWR is the right call when the data is read-heavy, changes slowly, and availability matters more than freshness: a homepage, a product listing, a configuration snapshot.

The `Cache` class above is a comparison harness, not a production cache. It has
no maximum size and never evicts expired entries proactively: an entry for a
key nobody asks about again sits in memory until the process ends. In
production, use Redis or Valkey with a `maxmemory` policy for the store,
and keep the coordination logic, jitter, single-flight, and the two
deadlines, which is where the stampede protection actually lives.

The wiring for the recommended default, all three together, looks like this:

```python
def product_lookup_example() -> None:
    """How the cache looks wired into a service. Not run by main()."""
    import random

    cache = Cache(rng=random.Random(20261013))

    def load_product(product_id: str):
        # The expensive read: database query, downstream call, render.
        return {"id": product_id, "price_cents": 1999}

    def get_product(product_id: str):
        return cache.get(
            f"product:{product_id}",
            lambda: load_product(product_id),
            ttl=3600.0,
            jitter=0.1,          # spread expiry across 3240..3960s
            stale_grace=300.0,   # serve stale up to 5 minutes past expiry
            wait_timeout=5.0,    # never block on a hung loader forever
        )

    assert get_product("42") == {"id": "42", "price_cents": 1999}
```

## Failure modes

| Mistake | What the reader sees | Cause | Fix |
| :--- | :--- | :--- | :--- |
| Coalescing with no timeout | One hung loader wedges every waiter; the outage spreads from the origin to every caller | The wait has no bound, so a loader that never returns holds all waiters forever | Always pass `wait_timeout`; treat repeated timeouts as a loader-health signal, not as a reason to raise the timeout |
| SWR with no staleness bound | Stale data served forever once the loader starts failing | A failed refresh extends the window, or there is no `stale_until` at all, so the stale entry never dies | Keep a hard `stale_until`; never extend it on refresh failure; alert on `refresh_failures` |
| Jitter that does not spread | Expiry still synchronized; the stampede happens on schedule | The same TTL on every key, or jitter applied at read time instead of write time, or a shared seed producing identical TTLs | Jitter once per key at write time with an unseeded or per-process RNG; verify the spread, as the test does |
| Shared key across tenants | One tenant's data served to another | A single-flight call shared by all tenants returns the leader's value to waiters from other tenants | Key by tenant: `tenant:{id}:product:{id}`. Single-flight shares results, so the key is a trust boundary |
| Cold start | A new cache node stampedes on first traffic | None of the three defenses helps an empty cache; every key is a miss | Prewarm new nodes before they serve traffic, as AWS's caching guide recommends; start with the hottest keys |
| Stale data after a write | Readers see the old value until expiry, even after an update | The cache is only invalidated by time, not by writes | Delete the key on write (`invalidate`), or write through. Invalidation ordering is the same problem the [transactional outbox](/posts/transactional-outbox-reliable-events-without-dual-writes/) solves for events: update the source of truth and the cache in an order that cannot strand a stale entry |

## Proving it works

The shipped tests run the real thing: 32 threads, a fake clock for expiry, and a slow loader. They assert the exact numbers quoted above, plus the failure behavior: a failed load is shared, not retried per waiter; a hung loader produces `CacheTimeoutError` for the waiter and the value still lands; a failed background refresh leaves stale data serving until the grace window ends and no longer. The Redis lock tests run against fakeredis and assert that only the lock owner can release, and that an expired lock cannot be released by its original holder.

```console
$ python3 -m unittest discover
Ran 18 tests in 1.9s

OK
$ python3 demo.py
baseline:        loads=32 (32 threads, no defense)
single-flight:   loads=1 waits=31 distinct_results=1 (32 threads, 1 load)
stale-while-rev: loads=1 stale_served=32 refreshes=1 distinct_results=1 (32 threads, all served the stale v1)
jitter:          expiry spread measured in test_cache.py (200 keys, ttl=3600, spread=0.1)
```

## Operating it

These are the counters the `Stats` class already emits. Export them with your metrics library's names and alert on the failure signals, not the happy path.

- `cache_loads_total`: loader invocations. A spike here is a stampede in progress or a mass expiry.
- `cache_stale_served_total`: stale serves. A sustained rise means the loader is failing or slow; it is the earliest signal that the origin is in trouble.
- `cache_refresh_failures_total`: failed background refreshes. Alert if it is nonzero for more than one grace window: the stale data is about to expire into synchronous loads.
- `cache_timeouts_total`: single-flight waiters that gave up. Alert on any sustained nonzero value: a loader is hanging.
- `cache_coalesced_waits_total`: waiters that shared a load. High values are healthy (the defense working); zero during a traffic spike means the defense is off.
- `cache_hits_total` and the loader's own latency histogram: the loader's p99 sets the single-flight timeout and the refresh budget. If p99 loader latency exceeds `stale_grace`, SWR degrades to synchronous loads for most callers, and the grace window needs raising or the loader needs fixing.

When the loader fails, do not retry it in a tight loop from 32 threads. Retry with [backoff and jitter](/posts/retries-with-exponential-backoff-and-jitter/) from the single-flight leader only, and let the waiters share the outcome.

## Redis: distributed single-flight

In one process, a lock in memory is enough. Across processes, the single-flight lock has to live in the shared store. The mapping from the in-memory design to Redis commands is:

| Piece | In memory | In Redis |
| :--- | :--- | :--- |
| Entry with two deadlines | `Entry(fresh_until, stale_until)` | One JSON value per key, or a hash with `value`, `fresh_until`, `stale_until` fields |
| Store with hard expiry | Dict entry | `SET key json EX <seconds until stale_until>` |
| Single-flight lock | Per-key `_Call` event | `SET lock:{key} {token} NX PX {timeout}` |
| Lock release | `finally` block | Lua compare-and-delete: delete only if the stored token is ours |
| TTL jitter | `jittered_ttl` at write time | Same function, applied before `SET` |

The lock is the only piece with a sharp edge, so it ships as code. Note the two properties that make it safe: the lock always has a timeout (`PX`), so a crashed holder cannot wedge the key forever, and release is a Lua script that deletes only when the token matches, so a holder whose lock expired cannot delete the next holder's lock.

```python
RELEASE_LUA = (
    "if redis.call('get', KEYS[1]) == ARGV[1] then "
    "return redis.call('del', KEYS[1]) else return 0 end"
)


class LockNotAcquired(RuntimeError):
    """Another process already holds the lock."""


class RedisLock:
    """A short-lived Redis lock for one load of one cache key."""

    def __init__(self, client, key: str, *, px_ms: int = 30_000, token: str | None = None) -> None:
        self._client = client
        self._key = key
        self._px_ms = px_ms
        self._token = token or secrets.token_hex(16)
        self._held = False

    @property
    def token(self) -> str:
        return self._token

    def acquire(self) -> bool:
        """Try to take the lock once. Returns False instead of blocking."""
        acquired = bool(self._client.set(self._key, self._token, nx=True, px=self._px_ms))
        self._held = acquired
        return acquired

    def release(self) -> bool:
        """Release only if we still hold the lock. Returns True if deleted."""
        deleted = bool(self._client.eval(RELEASE_LUA, 1, self._key, self._token))
        self._held = False
        return deleted

    def __enter__(self) -> "RedisLock":
        if not self.acquire():
            raise LockNotAcquired(f"lock already held: {self._key}")
        return self

    def __exit__(self, *exc) -> None:
        if self._held:
            self.release()
        return None
```

Redis also offers a different answer to the whole problem: server-assisted client-side caching, where the server tracks which keys each client has read and pushes invalidation messages when they change. That removes the expiry question entirely for data that changes by writes. It does not remove the stampede question: an invalidated key still misses on every client at once, and the first miss after invalidation still needs coalescing or SWR. Treat tracking as a complement to these defenses, not a replacement.

## Trade-offs and alternatives

Do not use SWR where freshness is contractual. A balance, a permission check, an inventory count: serving a stale value there is a correctness bug, not a performance win. Single-flight is the right defense for those keys, with a timeout and an error path the caller can act on.

Do not use single-flight where the load is cheap. If the loader is a sub-millisecond local computation, the lock bookkeeping costs more than the duplicate loads. Jitter alone is enough there.

Alternatives worth knowing, with the condition under which each wins:

- **Write-through caching**: update the cache when the data changes, instead of invalidating or expiring it. Wins when writes are rare and go through one code path; loses when writes fan out across services that forget to update the cache.
- **Prewarming**: fill the cache before a node serves traffic. Wins for cold starts and deploys; loses as a steady-state defense, because it does nothing for expiry-driven stampedes.
- **Client-side caching with server-assisted invalidation** (Redis tracking): wins when data changes by writes and every client needs to hear about it fast; loses when the invalidation itself fans out into a stampede, which it can.

The recommendation: jitter on every key, single-flight on every load, SWR wherever the freshness contract allows it. That is the default stack in the wiring example above. Measure the four counters, alert on the failure signals, and set `stale_grace` from how stale the data is allowed to be, not from how slow the loader is.

## Checklist

- [ ] Every cache write uses a jittered TTL, applied once per key at write time.
- [ ] Every load goes through single-flight, with a wait timeout set from measured loader p99.
- [ ] SWR entries have a hard `stale_until`; a failed refresh never extends it.
- [ ] Cache keys include the tenant. Single-flight shares results, so the key is a trust boundary.
- [ ] The loader's failure is shared with waiters, not retried once per waiter.
- [ ] `refresh_failures` and `timeouts` have alerts; `stale_served` is graphed.
- [ ] New cache nodes are prewarmed before they serve traffic.
- [ ] Writes invalidate or write through; time expiry is not the only invalidation path.

## References

- M. Nottingham, [HTTP Cache-Control Extensions for Stale Content (RFC 5861)](https://www.rfc-editor.org/rfc/rfc5861.html), IETF, 2010. Defines `stale-while-revalidate` and `stale-if-error`.
- Redis, [Redis 8.10.2 release notes](https://github.com/redis/redis/releases/tag/8.10.2), 2026. Current Redis release, a security release.
- Valkey, [Valkey 9.1.2 release notes](https://github.com/valkey-io/valkey/releases/tag/9.1.2), 2026. Current Valkey release, a security release.
- Redis, [Client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/), 2026. Server-assisted invalidation via tracking.
- Go, [`singleflight` package documentation](https://pkg.go.dev/golang.org/x/sync/singleflight), 2026. Duplicate function call suppression: one in-flight execution per key.
- AWS, [Caching Best Practices](https://aws.amazon.com/caching/best-practices/), 2026. Cache-aside, the thundering herd, prewarming, and TTL randomness.
