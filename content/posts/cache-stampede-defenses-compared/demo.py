"""Run the three defenses against the same stampede and print the numbers.

Every scenario: 32 threads, one hot key, one slow loader (300ms), one
shared cache. The baseline has no defense; the other three each add one.
The 300ms load window matters: after the start barrier releases all 32
threads, every thread must reach its cache check before the first load
finishes and stores, or the baseline would undercount. On this machine
32 threads start within a few milliseconds, so 300ms is a wide margin.

Run with ``python3 demo.py`` from this folder. Output is the measurement
the article quotes.
"""

from __future__ import annotations

import threading
import time

from cache import Cache, FakeClock

THREADS = 32
LOAD_SECONDS = 0.3


def _stampede(cache: Cache, get_fn, loader) -> list:
    barrier = threading.Barrier(THREADS)
    results: list = [None] * THREADS
    errors: list = [None] * THREADS

    def _worker(i: int) -> None:
        barrier.wait(timeout=10)
        try:
            results[i] = get_fn(loader)
        except BaseException as exc:  # noqa: BLE001 - reported, not swallowed
            errors[i] = exc

    workers = [threading.Thread(target=_worker, args=(i,)) for i in range(THREADS)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=30)
    assert all(error is None for error in errors), errors
    return results


def _counting_loader(calls: list, value: str):
    def _load():
        calls.append(1)
        time.sleep(LOAD_SECONDS)
        return value

    return _load


def run_baseline() -> None:
    cache = Cache()
    calls: list = []
    _stampede(cache, lambda loader: cache.get_baseline("product:42", loader, ttl=60.0),
               _counting_loader(calls, "v1"))
    stats = cache.stats.snapshot()
    print(f"baseline:        loads={stats['loads']} (32 threads, no defense)")


def run_singleflight() -> None:
    cache = Cache()
    calls: list = []
    results = _stampede(
        cache,
        lambda loader: cache.get("product:42", loader, ttl=60.0),
        _counting_loader(calls, "v1"),
    )
    stats = cache.stats.snapshot()
    print(f"single-flight:   loads={stats['loads']} waits={stats['coalesced_waits']} "
          f"distinct_results={len(set(results))} (32 threads, 1 load)")


def run_swr() -> None:
    clock = FakeClock()
    cache = Cache(clock=clock)
    calls: list = []
    cache.get("product:42", _counting_loader(calls, "v1"), ttl=60.0, stale_grace=300.0)
    seeded_loads = cache.stats.snapshot()["loads"]
    clock.advance(61.0)  # past fresh, inside the 300s stale grace window
    results = _stampede(
        cache,
        lambda loader: cache.get("product:42", loader, ttl=60.0, stale_grace=300.0),
        _counting_loader(calls, "v2"),
    )
    deadline = time.monotonic() + 5
    while cache.stats.snapshot()["refreshes"] < 1 and time.monotonic() < deadline:
        time.sleep(0.005)
    stats = cache.stats.snapshot()
    print(f"stale-while-rev: loads={stats['loads'] - seeded_loads} "
          f"stale_served={stats['stale_served']} refreshes={stats['refreshes']} "
          f"distinct_results={len(set(results))} (32 threads, all served the stale v1)")


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


def main() -> None:
    run_baseline()
    run_singleflight()
    run_swr()
    print("jitter:          expiry spread measured in test_cache.py (200 keys, ttl=3600, spread=0.1)")


if __name__ == "__main__":
    main()
