"""Cache-stampede defenses: TTL jitter, single-flight coalescing, stale-while-revalidate.

A cache stampede (also called a thundering herd or dogpile) happens when a
popular cache entry expires and many concurrent requests all miss at once.
Each one runs the same expensive load against the origin, so the cache that
was supposed to protect the origin becomes the thing that synchronises the
attack on it.

This module implements the three standard defenses against that failure,
all in one small class so their behaviour can be compared honestly:

- TTL jitter: spread expiry times so entries do not all die together.
- Single-flight coalescing: when N callers miss the same key at the same
  time, exactly one of them runs the loader and the rest share its result.
  Named after Go's ``golang.org/x/sync/singleflight`` package.
- Stale-while-revalidate (SWR): after an entry goes stale, keep serving
  the old value while exactly one background refresh runs. The idea comes
  from RFC 5861's ``stale-while-revalidate`` Cache-Control extension.

The cache is in-memory and backend-agnostic on purpose: the defenses are
about coordination, and coordination is easiest to test with a fake clock
and real threads. The companion ``redis_lock.py`` shows the one piece that
changes when the cache is shared across processes: the single-flight lock
moves into Redis (``SET key token NX PX`` plus a Lua compare-and-delete
release).

Versions pinned by the article: Python 3.12 standard library only for this
file; Redis 8.10.2 / Valkey 9.1.2 for the Redis mapping.
"""

from __future__ import annotations

import random
import threading
import time
from dataclasses import dataclass, field


class CacheTimeoutError(TimeoutError):
    """A single-flight waiter gave up before the leader finished loading."""


class CacheLoaderError(RuntimeError):
    """The loader failed. Raised to every caller that shared the load."""


@dataclass
class Entry:
    """One cached value with two deadlines.

    ``fresh_until``: serve the value as fresh before this time.
    ``stale_until``: after ``fresh_until``, serve the value as stale (and
    refresh in the background) until this time. Past ``stale_until`` the
    value is dead: the next caller loads synchronously.
    """

    value: object
    fresh_until: float
    stale_until: float


@dataclass
class Stats:
    """Counters for everything the article measures. All updates are locked."""

    hits: int = 0
    loads: int = 0
    stale_served: int = 0
    coalesced_waits: int = 0
    timeouts: int = 0
    refreshes: int = 0
    refresh_failures: int = 0
    loader_errors: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def increment(self, name: str) -> None:
        with self._lock:
            setattr(self, name, getattr(self, name) + 1)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "hits": self.hits,
                "loads": self.loads,
                "stale_served": self.stale_served,
                "coalesced_waits": self.coalesced_waits,
                "timeouts": self.timeouts,
                "refreshes": self.refreshes,
                "refresh_failures": self.refresh_failures,
                "loader_errors": self.loader_errors,
            }


class SystemClock:
    """The real clock. Swapped for FakeClock in tests."""

    def now(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class FakeClock:
    """A clock the test drives by hand. ``sleep`` advances it instantly."""

    def __init__(self, start: float = 0.0) -> None:
        self._now = start
        self._lock = threading.Lock()

    def now(self) -> float:
        with self._lock:
            return self._now

    def sleep(self, seconds: float) -> None:
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        with self._lock:
            self._now += seconds


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


class _Call:
    """One in-flight load shared by a leader and its waiters."""

    def __init__(self) -> None:
        self.done = threading.Event()
        self.value: object = None
        self.error: BaseException | None = None


class Cache:
    """An in-memory cache with stampede defenses.

    ``clock`` is a SystemClock by default and a FakeClock in tests, so
    expiry is deterministic. ``rng`` is a ``random.Random``; pass a seeded
    one for reproducible jitter. ``stats`` counts what happened.
    """

    def __init__(
        self,
        *,
        clock: SystemClock | FakeClock | None = None,
        rng: random.Random | None = None,
        stats: Stats | None = None,
    ) -> None:
        self._clock = clock or SystemClock()
        self._rng = rng or random.Random()
        self._stats = stats or Stats()
        self._entries: dict[str, Entry] = {}
        self._calls: dict[str, _Call] = {}
        self._refreshing: set[str] = set()
        self._guard = threading.Lock()

    @property
    def stats(self) -> Stats:
        return self._stats

    def get_baseline(self, key: str, loader, ttl: float):
        """Plain cache-aside with no defense. Used to measure the stampede."""
        entry = self._entries.get(key)
        if entry is not None and self._clock.now() < entry.fresh_until:
            self._stats.increment("hits")
            return entry.value
        self._stats.increment("loads")
        value = loader()
        now = self._clock.now()
        self._entries[key] = Entry(value, now + ttl, now + ttl)
        return value

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

    def invalidate(self, key: str) -> None:
        """Drop ``key``. Call this when the underlying data changes."""
        self._entries.pop(key, None)

    def _store(self, key, value, ttl, jitter, stale_grace) -> None:
        now = self._clock.now()
        fresh_for = jittered_ttl(ttl, jitter, self._rng)
        self._entries[key] = Entry(value, now + fresh_for, now + fresh_for + stale_grace)

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
