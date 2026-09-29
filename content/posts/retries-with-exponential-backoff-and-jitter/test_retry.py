"""Tests for retry.py. Run with: python3 -W error::DeprecationWarning -m unittest test_retry -v"""

from __future__ import annotations

import random
import threading
import unittest

from retry import (
    PermanentError,
    RetryExhausted,
    ServiceError,
    TokenBucket,
    TransientError,
    classify,
    with_retries,
)


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def sleep(self, secs: float) -> None:
        assert secs >= 0, f"negative sleep {secs}"
        self.now += secs


def scripted(failures, clock):
    """Build an fn(remaining) that raises each failure in turn, then succeeds."""
    calls = []

    def fn(remaining):
        calls.append(remaining)
        if failures:
            exc = failures.pop(0)
            if isinstance(exc, float):
                # cooperative work: consume time, but never more than remaining
                work = min(exc, remaining) if remaining is not None else exc
                clock.now += work
                raise TransientError("slow dependency")
            raise exc
        return "ok"

    fn.calls = calls
    return fn


class ClassifyTests(unittest.TestCase):
    def test_explicit_markers(self):
        self.assertEqual(classify(TransientError("x")), "transient")
        self.assertEqual(classify(PermanentError("x")), "permanent")

    def test_network_failures_are_transient(self):
        self.assertEqual(classify(ConnectionError("reset")), "transient")
        self.assertEqual(classify(TimeoutError("timed out")), "transient")

    def test_code_wins_over_status(self):
        # 400 RequestTimeout is transient even though 400 is a client error.
        self.assertEqual(
            classify(ServiceError("t/o", status=400, code="RequestTimeout")),
            "transient")
        # 400 ValidationException is permanent.
        self.assertEqual(
            classify(ServiceError("bad", status=400, code="ValidationException")),
            "permanent")
        # A listed non-retryable code wins even over a 5xx status.
        self.assertEqual(
            classify(ServiceError("bad", status=503,
                                   code="ValidationException")),
            "permanent")
        # A 5xx with a throttling code is throttling, not transient.
        self.assertEqual(
            classify(ServiceError("slow", status=503, code="Throttling")),
            "throttling")
        # An unrecognized code falls back to the status rules.
        self.assertEqual(
            classify(ServiceError("weird", status=503, code="SomethingNew")),
            "transient")
        self.assertEqual(
            classify(ServiceError("weird", status=400, code="SomethingNew")),
            "permanent")

    def test_status_fallback(self):
        self.assertEqual(classify(ServiceError("nf", status=404)), "permanent")
        self.assertEqual(classify(ServiceError("bad", status=400)), "permanent")
        self.assertEqual(classify(ServiceError("rl", status=429)), "throttling")
        self.assertEqual(classify(ServiceError("to", status=408)), "transient")
        self.assertEqual(classify(ServiceError("down", status=500)), "transient")
        self.assertEqual(classify(ServiceError("down", status=502)), "transient")
        self.assertEqual(classify(ServiceError("down", status=503)), "transient")
        self.assertEqual(classify(ServiceError("down", status=504)), "transient")
        # 501 is not in the SDK's transient status list.
        self.assertEqual(classify(ServiceError("ni", status=501)), "permanent")

    def test_unknown_is_permanent(self):
        self.assertEqual(classify(ValueError("huh")), "permanent")


class BucketTests(unittest.TestCase):
    def test_take_and_empty(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=2, refill_per_second=0.0, clock=clock)
        self.assertTrue(bucket.take())
        self.assertTrue(bucket.take())
        self.assertFalse(bucket.take())

    def test_continuous_refill(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=2, refill_per_second=1.0, clock=clock)
        self.assertTrue(bucket.take())
        self.assertTrue(bucket.take())
        self.assertFalse(bucket.take())
        clock.now += 1.5  # 1.5 tokens refill
        self.assertTrue(bucket.take())
        self.assertFalse(bucket.take())  # only 0.5 left

    def test_refill_capped_at_capacity(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=2, refill_per_second=100.0, clock=clock)
        clock.now += 3600.0
        self.assertAlmostEqual(bucket.available(), 2.0)

    def test_successes_do_not_add_tokens(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=1, refill_per_second=0.0, clock=clock)
        self.assertTrue(bucket.take())
        # A success happening here must not refill the bucket.
        self.assertFalse(bucket.take())

    def test_thread_safe(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=50, refill_per_second=0.0, clock=clock)
        results = []

        def hammer():
            results.append(bucket.take())

        threads = [threading.Thread(target=hammer) for _ in range(200)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(sum(results), 50)


class RetryTests(unittest.TestCase):
    def test_success_first_try(self):
        clock = FakeClock()
        fn = scripted([], clock)
        self.assertEqual(
            with_retries(fn, clock=clock, sleep=clock.sleep), "ok")
        self.assertEqual(len(fn.calls), 1)
        self.assertIsNone(fn.calls[0])  # no deadline configured

    def test_retries_transient_then_succeeds(self):
        clock = FakeClock()
        fn = scripted([TransientError("boom")], clock)
        rng = random.Random(7)
        self.assertEqual(
            with_retries(fn, clock=clock, sleep=clock.sleep, rng=rng), "ok")
        self.assertEqual(len(fn.calls), 2)

    def test_permanent_error_not_retried(self):
        clock = FakeClock()
        fn = scripted([ServiceError("bad", status=400,
                                    code="ValidationException")], clock)
        with self.assertRaises(RetryExhausted) as ctx:
            with_retries(fn, clock=clock, sleep=clock.sleep)
        self.assertEqual(ctx.exception.reason, "permanent")
        self.assertEqual(len(fn.calls), 1)

    def test_400_request_timeout_is_retried(self):
        clock = FakeClock()
        fn = scripted([ServiceError("t/o", status=400, code="RequestTimeout")],
                      clock)
        rng = random.Random(7)
        self.assertEqual(
            with_retries(fn, clock=clock, sleep=clock.sleep, rng=rng), "ok")
        self.assertEqual(len(fn.calls), 2)

    def test_max_attempts(self):
        clock = FakeClock()
        fn = scripted([TransientError("x")] * 10, clock)
        with self.assertRaises(RetryExhausted) as ctx:
            with_retries(fn, max_attempts=3, clock=clock, sleep=clock.sleep,
                         rng=random.Random(1))
        self.assertEqual(ctx.exception.reason, "max_attempts")
        self.assertEqual(len(fn.calls), 3)

    def test_empty_budget_stops_retries(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=1, refill_per_second=0.0, clock=clock)
        fn = scripted([TransientError("x")] * 10, clock)
        with self.assertRaises(RetryExhausted) as ctx:
            with_retries(fn, max_attempts=5, budget=bucket, clock=clock,
                         sleep=clock.sleep, rng=random.Random(1))
        self.assertEqual(ctx.exception.reason, "budget")
        self.assertEqual(len(fn.calls), 2)  # initial + one budgeted retry

    def test_budget_not_spent_when_deadline_blocks_retry(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=1, refill_per_second=0.0, clock=clock)
        fn = scripted([TransientError("x")] * 10, clock)
        stub = random.Random()
        stub.uniform = lambda a, b: b  # always the longest possible wait
        with self.assertRaises(RetryExhausted) as ctx:
            with_retries(fn, max_attempts=5, budget=bucket, total_timeout=0.001,
                         base_delay=60.0, clock=clock, sleep=clock.sleep,
                         rng=stub)
        self.assertEqual(ctx.exception.reason, "deadline")
        # The retry never ran, so its token was never consumed.
        self.assertTrue(bucket.take())

    # [block demo]
    def test_deadline_caps_helper_time(self):
        clock = FakeClock()
        # Each attempt cooperatively consumes up to the remaining time.
        fn = scripted([2.0, 2.0, 2.0, 2.0], clock)
        with self.assertRaises(RetryExhausted) as ctx:
            with_retries(fn, max_attempts=10, total_timeout=5.0, clock=clock,
                         sleep=clock.sleep, rng=random.Random(3))
        self.assertEqual(ctx.exception.reason, "deadline")
        # Attempts received non-increasing remaining times within the deadline.
        for remaining in fn.calls:
            self.assertLessEqual(remaining, 5.0)
        self.assertEqual(
            sorted(fn.calls, reverse=True), fn.calls)
        # Helper-controlled time (sleeps) plus cooperative work stayed inside
        # the deadline; the helper never started a wait past it.
        self.assertLessEqual(clock.now - 1000.0, 5.0)
    # [/block demo]

    def test_non_idempotent_runs_exactly_once(self):
        clock = FakeClock()
        fn = scripted([TransientError("x"), TransientError("y")], clock)
        with self.assertRaises(RetryExhausted) as ctx:
            with_retries(fn, idempotent=False, clock=clock, sleep=clock.sleep,
                         rng=random.Random(1))
        self.assertEqual(ctx.exception.reason, "not_idempotent")
        self.assertIsInstance(ctx.exception.last_exc, TransientError)
        # Exactly one attempt ran: the failure was never retried.
        self.assertEqual(len(fn.calls), 1)

    def test_non_idempotent_empty_key_runs_once(self):
        clock = FakeClock()
        fn = scripted([TransientError("x")], clock)
        with self.assertRaises(RetryExhausted) as ctx:
            with_retries(fn, idempotent=False, idempotency_key="",
                         clock=clock, sleep=clock.sleep,
                         rng=random.Random(1))
        self.assertEqual(ctx.exception.reason, "not_idempotent")
        self.assertEqual(len(fn.calls), 1)

    def test_non_idempotent_success_returns(self):
        clock = FakeClock()
        fn = scripted([], clock)
        self.assertEqual(
            with_retries(fn, idempotent=False, clock=clock,
                         sleep=clock.sleep), "ok")
        self.assertEqual(len(fn.calls), 1)

    def test_non_idempotent_with_key_allowed(self):
        clock = FakeClock()
        fn = scripted([TransientError("x")], clock)
        self.assertEqual(
            with_retries(fn, idempotent=False, idempotency_key="k-1",
                         clock=clock, sleep=clock.sleep,
                         rng=random.Random(1)),
            "ok")

    def test_server_directed_delay_overrides_backoff(self):
        # The server knows when it will have capacity; honor it.
        clock = FakeClock()
        delays = []
        fn = scripted(
            [ServiceError("slow", status=429, retry_after=2.0),
             ServiceError("slow", status=429, retry_after=2.0)], clock)
        stub = random.Random()
        stub.uniform = lambda a, b: b  # raw backoff, no jitter
        self.assertEqual(
            with_retries(fn, max_attempts=3, base_delay=0.5, max_delay=100.0,
                         throttling_base_delay=0.5, clock=clock,
                         sleep=delays.append, rng=stub), "ok")
        # Raw backoffs would be 0.5 and 1.0; the server's 2 s wins each time.
        self.assertEqual(delays, [2.0, 2.0])

    def test_server_directed_delay_never_below_backoff(self):
        clock = FakeClock()
        delays = []
        fn = scripted(
            [ServiceError("slow", status=429, retry_after=0.01),
             ServiceError("slow", status=429, retry_after=0.01)], clock)
        stub = random.Random()
        stub.uniform = lambda a, b: b
        self.assertEqual(
            with_retries(fn, max_attempts=3, base_delay=0.5, max_delay=100.0,
                         throttling_base_delay=0.5, clock=clock,
                         sleep=delays.append, rng=stub), "ok")
        # The 10 ms server hint is below the computed backoff, so the
        # backoff (0.5, 1.0) wins.
        self.assertEqual(delays, [0.5, 1.0])

    def test_server_directed_delay_capped_at_backoff_plus_five(self):
        clock = FakeClock()
        delays = []
        fn = scripted([ServiceError("slow", status=429, retry_after=60.0)],
                      clock)
        stub = random.Random()
        stub.uniform = lambda a, b: b
        self.assertEqual(
            with_retries(fn, max_attempts=2, base_delay=0.5, max_delay=100.0,
                         throttling_base_delay=0.5, clock=clock,
                         sleep=delays.append, rng=stub), "ok")
        # The 60 s server hint is clamped at backoff + 5 s = 5.5 s.
        self.assertEqual(delays, [5.5])

    def test_server_directed_delay_respects_deadline(self):
        clock = FakeClock()
        fn = scripted([ServiceError("slow", status=429, retry_after=60.0)],
                      clock)
        stub = random.Random()
        stub.uniform = lambda a, b: b
        with self.assertRaises(RetryExhausted) as ctx:
            with_retries(fn, max_attempts=2, total_timeout=1.0,
                         base_delay=0.5, max_delay=100.0,
                         throttling_base_delay=0.5, clock=clock,
                         sleep=clock.sleep, rng=stub)
        # The clamped 5.5 s wait does not fit in the 1 s deadline.
        self.assertEqual(ctx.exception.reason, "deadline")
        self.assertEqual(len(fn.calls), 1)

    def test_backoff_is_capped(self):
        clock = FakeClock()
        delays = []
        fn = scripted([TransientError("x")] * 10, clock)
        with self.assertRaises(RetryExhausted):
            with_retries(fn, max_attempts=6, base_delay=10.0, max_delay=0.5,
                         clock=clock, sleep=delays.append,
                         rng=random.Random(1))
        self.assertTrue(delays)
        for d in delays:
            self.assertLessEqual(d, 0.5)

    def test_exponential_shape(self):
        # A stub rng returning the top of the range exposes the raw backoff.
        clock = FakeClock()
        delays = []
        fn = scripted([TransientError("x")] * 10, clock)
        stub = random.Random()
        stub.uniform = lambda a, b: b
        with self.assertRaises(RetryExhausted):
            with_retries(fn, max_attempts=5, base_delay=0.5, max_delay=100.0,
                         clock=clock, sleep=delays.append, rng=stub)
        self.assertEqual(delays, [0.5, 1.0, 2.0, 4.0])

    def test_full_jitter_range_and_determinism(self):
        clock = FakeClock()
        run1, run2 = [], []
        for out in (run1, run2):
            fn = scripted([TransientError("x")] * 10, clock)
            with self.assertRaises(RetryExhausted):
                with_retries(fn, max_attempts=6, base_delay=1.0, max_delay=8.0,
                             clock=clock, sleep=out.append,
                             rng=random.Random(99))
        for d in run1:
            self.assertGreaterEqual(d, 0.0)
            self.assertLessEqual(d, 8.0)
        self.assertEqual(run1, run2)  # same seed, same schedule


if __name__ == "__main__":
    unittest.main()
