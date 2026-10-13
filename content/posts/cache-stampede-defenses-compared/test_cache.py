"""Tests for the three stampede defenses. Standard library only.

Run: ``python3 -m unittest discover -v`` from this folder.
Every test uses FakeClock except the multi-threaded stampede tests, which
use the real clock (threads cannot share a fake clock meaningfully) and a
300ms loader so all 32 threads pile up on the same miss.
"""

import random
import threading
import time
import unittest

from cache import (
    Cache,
    CacheTimeoutError,
    FakeClock,
    Stats,
    jittered_ttl,
)

THREADS = 32
LOAD_SECONDS = 0.3


def stampede(cache, get_fn, loader):
    """Release 32 threads on one key at once; return (results, errors)."""
    barrier = threading.Barrier(THREADS)
    results = [None] * THREADS
    errors = [None] * THREADS

    def worker(i):
        barrier.wait(timeout=10)
        try:
            results[i] = get_fn(loader)
        except BaseException as exc:  # noqa: BLE001 - collected for the assertion
            errors[i] = exc

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(THREADS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    return results, errors


def counting_loader(calls, value, delay=LOAD_SECONDS):
    def load():
        calls.append(1)
        if delay:
            time.sleep(delay)
        return value

    return load


def wait_for(predicate, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return predicate()


class TestJitter(unittest.TestCase):
    def test_spread_is_bounded_and_wide(self):
        rng = random.Random(20261013)
        ttls = [jittered_ttl(3600.0, 0.1, rng) for _ in range(200)]
        self.assertTrue(all(3240.0 <= ttl <= 3960.0 for ttl in ttls))
        self.assertGreater(max(ttls) - min(ttls), 600.0)

    def test_zero_spread_is_exact(self):
        rng = random.Random(1)
        self.assertEqual(jittered_ttl(60.0, 0.0, rng), 60.0)

    def test_invalid_arguments_rejected(self):
        rng = random.Random(1)
        with self.assertRaises(ValueError):
            jittered_ttl(0.0, 0.1, rng)
        with self.assertRaises(ValueError):
            jittered_ttl(60.0, 1.0, rng)
        with self.assertRaises(ValueError):
            jittered_ttl(60.0, -0.1, rng)

    def test_jittered_entries_expire_at_different_times(self):
        clock = FakeClock()
        cache = Cache(clock=clock, rng=random.Random(20261013))
        for i in range(50):
            cache.get(f"key:{i}", lambda: "v", ttl=3600.0, jitter=0.1)
        clock.advance(3400.0)
        expired = sum(
            1 for i in range(50) if cache.get(f"key:{i}", lambda: "v2", ttl=3600.0, jitter=0.1) == "v2"
        )
        self.assertGreater(expired, 0)
        self.assertLess(expired, 50)


class TestBaseline(unittest.TestCase):
    def test_baseline_loads_once_per_thread(self):
        cache = Cache()
        calls: list = []
        results, errors = stampede(
            cache,
            lambda loader: cache.get_baseline("k", loader, ttl=60.0),
            counting_loader(calls, "v1"),
        )
        self.assertEqual(errors, [None] * THREADS)
        self.assertEqual(len(calls), THREADS)
        self.assertEqual(set(results), {"v1"})


class TestSingleFlight(unittest.TestCase):
    def test_32_threads_one_load(self):
        cache = Cache()
        calls: list = []
        results, errors = stampede(
            cache, lambda loader: cache.get("k", loader, ttl=60.0), counting_loader(calls, "v1")
        )
        self.assertEqual(errors, [None] * THREADS)
        self.assertEqual(len(calls), 1)
        self.assertEqual(cache.stats.snapshot()["coalesced_waits"], THREADS - 1)
        self.assertEqual(set(results), {"v1"})

    def test_failed_load_is_shared_not_retried_per_waiter(self):
        cache = Cache()
        calls: list = []

        def failing():
            calls.append(1)
            time.sleep(LOAD_SECONDS)
            raise RuntimeError("origin down")

        results, errors = stampede(cache, lambda loader: cache.get("k", loader, ttl=60.0), failing)
        self.assertEqual(len(calls), 1)
        self.assertTrue(all(isinstance(e, RuntimeError) for e in errors))

    def test_waiter_timeout_does_not_wedge_on_hung_loader(self):
        cache = Cache()
        release = threading.Event()
        calls: list = []

        def hanging():
            calls.append(1)
            release.wait(timeout=10)
            return "v1"

        outcome: list = []

        def waiter():
            try:
                cache.get("k", hanging, ttl=60.0, wait_timeout=0.2)
            except CacheTimeoutError:
                outcome.append("timeout")

        leader = threading.Thread(target=lambda: cache.get("k", hanging, ttl=60.0))
        leader.start()
        self.assertTrue(
            wait_for(lambda: "k" in cache._calls), "leader never registered its call"
        )
        waiter_thread = threading.Thread(target=waiter)
        waiter_thread.start()
        waiter_thread.join(timeout=5)
        self.assertEqual(outcome, ["timeout"])
        self.assertEqual(cache.stats.snapshot()["timeouts"], 1)
        release.set()
        leader.join(timeout=5)
        self.assertEqual(cache.get("k", lambda: "v2", ttl=60.0), "v1")

    def test_singleflight_off_loads_per_thread(self):
        cache = Cache()
        calls: list = []
        results, errors = stampede(
            cache,
            lambda loader: cache.get("k", loader, ttl=60.0, singleflight=False),
            counting_loader(calls, "v1"),
        )
        self.assertEqual(errors, [None] * THREADS)
        self.assertEqual(len(calls), THREADS)


class TestStaleWhileRevalidate(unittest.TestCase):
    def test_stale_served_while_one_refresh_runs(self):
        clock = FakeClock()
        cache = Cache(clock=clock)
        cache.get("k", lambda: "v1", ttl=60.0, stale_grace=300.0)
        clock.advance(61.0)
        calls: list = []
        results, errors = stampede(
            cache,
            lambda loader: cache.get("k", loader, ttl=60.0, stale_grace=300.0),
            counting_loader(calls, "v2", delay=LOAD_SECONDS),
        )
        self.assertEqual(errors, [None] * THREADS)
        self.assertEqual(set(results), {"v1"})
        self.assertEqual(cache.stats.snapshot()["stale_served"], THREADS)
        self.assertTrue(wait_for(lambda: cache.stats.snapshot()["refreshes"] == 1))
        self.assertEqual(cache.get("k", lambda: "v3", ttl=60.0, stale_grace=300.0), "v2")

    def test_failed_refresh_keeps_stale_but_does_not_extend_it(self):
        clock = FakeClock()
        cache = Cache(clock=clock)
        cache.get("k", lambda: "v1", ttl=60.0, stale_grace=300.0)
        clock.advance(61.0)
        cache.get("k", lambda: (_ for _ in ()).throw(RuntimeError("origin down")),
                  ttl=60.0, stale_grace=300.0)
        self.assertTrue(wait_for(lambda: cache.stats.snapshot()["refresh_failures"] == 1))
        # Still inside the grace window: stale v1 keeps serving.
        self.assertEqual(
            cache.get("k", lambda: "v2", ttl=60.0, stale_grace=300.0), "v1"
        )
        # Past the grace window: the dead entry is gone, next caller loads fresh.
        clock.advance(300.0)
        self.assertEqual(
            cache.get("k", lambda: "v2", ttl=60.0, stale_grace=300.0), "v2"
        )

    def test_past_grace_loads_synchronously(self):
        clock = FakeClock()
        cache = Cache(clock=clock)
        cache.get("k", lambda: "v1", ttl=60.0, stale_grace=300.0)
        clock.advance(400.0)
        self.assertEqual(
            cache.get("k", lambda: "v2", ttl=60.0, stale_grace=300.0), "v2"
        )
        self.assertEqual(cache.stats.snapshot()["stale_served"], 0)


class TestInvalidate(unittest.TestCase):
    def test_invalidate_forces_reload(self):
        cache = Cache()
        self.assertEqual(cache.get("k", lambda: "v1", ttl=60.0), "v1")
        cache.invalidate("k")
        self.assertEqual(cache.get("k", lambda: "v2", ttl=60.0), "v2")


if __name__ == "__main__":
    unittest.main()
