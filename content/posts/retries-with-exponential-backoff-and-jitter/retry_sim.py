"""Seeded simulation behind the jitter-lanes figure.

Twenty-four clients hit a dependency at t=0, fail, and retry three times with
capped exponential backoff (base 1.0 s, cap 8.0 s). One run waits the full
backoff; the other applies full jitter. One seeded RNG drives every client,
so the run is deterministic and the figure is reproducible.

Reports the peak number of retry attempts landing in any 250 ms bucket, which
is the number the article quotes.
"""

from __future__ import annotations

import random

CLIENTS = 24
BASE_DELAY = 1.0
MAX_DELAY = 8.0
RETRIES = 3
BUCKET = 0.25
SEED = 7


def run(*, clients: int = CLIENTS, base: float = BASE_DELAY,
        cap: float = MAX_DELAY, retries: int = RETRIES,
        seed: int = SEED, jitter: bool) -> dict:
    """Simulate retry schedules; return per-bucket attempt counts and the peak."""
    rng = random.Random(seed)
    buckets: dict[int, int] = {}
    waves: list[list[float]] = [[] for _ in range(retries)]
    for _ in range(clients):
        t = 0.0
        for wave in range(retries):
            delay = min(cap, base * (2 ** wave))
            if jitter:
                delay = rng.uniform(0, delay)
            t += delay
            buckets[int(t // BUCKET)] = buckets.get(int(t // BUCKET), 0) + 1
            waves[wave].append(t)
    peak = max(buckets.values()) if buckets else 0
    return {
        "clients": clients,
        "base": base,
        "cap": cap,
        "retries": retries,
        "seed": seed,
        "jitter": jitter,
        "buckets": buckets,
        "waves": waves,
        "peak": peak,
        "attempts": clients * retries,
    }


def main() -> None:
    plain = run(jitter=False)
    jittered = run(jitter=True)
    print(f"clients={plain['clients']} base={plain['base']}s cap={plain['cap']}s "
          f"retries={plain['retries']} bucket={BUCKET}s")
    print(f"no jitter:   peak {plain['peak']} attempts per 250 ms "
          f"(seed {plain['seed']})")
    print(f"full jitter: peak {jittered['peak']} attempts per 250 ms "
          f"(seed {jittered['seed']})")
    for seed in (42, 123, 2026):
        alt = run(seed=seed, jitter=True)
        print(f"full jitter: peak {alt['peak']} attempts per 250 ms "
              f"(seed {seed})")


if __name__ == "__main__":
    main()
