---
title: "Retries with Exponential Backoff and Jitter"
description: >-
  Retries multiply across layers and synchronize recovery traffic, turning
  a blip into an outage. Tested Python code: error classification, capped
  backoff, full jitter, server-directed delays, retry budgets, and deadlines.
date: 2026-09-29 16:30:00 +0000
updated: 2026-09-29 17:04:08 +0000
author: ritesh
categories: [Distributed Systems, Reliability]
tags: [retries, exponential-backoff, jitter, resilience, python]
kind: Guide
draft: false
cover:
  image: cover.webp
  alt: A client request fanning out into synchronized retry waves on the left, spreading into scattered jittered attempts on the right, over a timeline with exponential backoff markers.
---

Your dependency hiccups for five seconds. Every instance of your service retries immediately, fails again, and retries again. The dependency recovers, and then a thousand synchronized clients slam it at the same instant. The five-second blip becomes a fifteen-minute outage, and the retry logic you added for resilience caused it. (This opening is an illustrative scenario; the numbers are chosen for effect, not measured.)

The obvious fixes each fail in a different way. Retry immediately and the clients form a thundering herd. Wait a fixed one second and they still wake up together, in lockstep, because they all failed at the same moment. Retry at every layer of the call chain and one user action becomes dozens of backend attempts. Retry every error and you burn quota on requests that can never succeed, or worse, you execute a charge twice.

This guide builds a retry helper that gets four decisions right: which failures deserve a retry, how long to wait between attempts, how much retrying the whole system can afford, and when to stop and report failure. The code is Python 3.12, standard library only, and ships next to this article with 29 tests. The design follows the AWS builders' library guidance on timeouts, retries, and backoff with jitter, the AWS Architecture Blog's comparison of jitter strategies, the retry behavior of the AWS SDKs, and the Google SRE book's chapter on cascading failures.

> [!NOTE]
> **In short**
> - Retry at exactly one layer of the call chain. Every additional retrying layer multiplies attempts: three layers with three retries each turn one call into 64 database attempts.
> - Wait with capped exponential backoff and full jitter: `uniform(0, min(cap, base * 2**retry))`. Unjittered backoff synchronizes recovery traffic; the AWS Architecture Blog reports over 50% fewer calls with jitter for 100 contending clients in its own simulation.
> - Classify by error code first, status second. A `400` with code `RequestTimeout` is transient; a `400` with code `ValidationException` is permanent. Never retry what you do not understand.
> - Bound total retrying with a shared token-bucket budget and a total deadline. Spend a budget token only on a retry that will actually run.
> - A non-idempotent operation without an idempotency key runs exactly once and is never retried; a failure raises `RetryExhausted` with reason `not_idempotent`.

## Retry at one layer

Every layer that retries multiplies the attempts of the layer above it. The Google SRE book works the example explicitly: the JavaScript client, the frontend, and the backend each retry three times. Three retries means four attempts per layer, and the database sees 4 x 4 x 4 = 64 attempts for a single user action. The AWS builders' library states the same rule directly, qualified to cheap calls: "for low-cost control-plane and data-plane operations, our best practice is to retry at a single point in the stack." Retrying at the top layer can waste work from earlier calls, which is why the qualifier matters; for low-cost operations the single retrying layer wins. My own recommendation on top of that: make the other layers fail fast with tight timeouts, so the designated layer is the only one deciding whether to retry.

![Two rows of boxes for the JavaScript client, frontend, backend, and database. Top row: every layer retries, one call becomes 64 database attempts. Bottom row: only the top layer retries, the database sees 4 attempts.](retry-amplification.svg "Retry at one layer: every retrying layer multiplies the attempts above it, 4 x 4 x 4 = 64 (Google SRE book); with retries at the top layer only and inner layers failing fast, the database sees 4 attempts."){: .figure}

The fix is organizational, not algorithmic. Designate exactly one layer as the retrying layer for each call chain, usually the outermost client, because it owns the user-facing deadline and has the most context for how long the whole operation may take. Every inner layer gets a tight timeout and no retries of its own: it fails fast and lets the designated layer decide. If you inherit a system where a sidecar, a service mesh, or an SDK already retries, count that as the one layer and turn yours off. Two layers that each retry "just twice" still multiply to nine attempts per call, and the multiplication hides inside latency percentiles until a blip exposes it.

## Jitter the backoff

When many clients fail at the same moment and back off by the same schedule, they recover in lockstep. Pure exponential backoff of 1, 2, 4 seconds means every client retries at t+1, t+2, t+4. The recovery traffic arrives as synchronized waves, and the first wave can knock the dependency over again just as it was recovering. The AWS Architecture Blog tested this directly and called backoff without jitter the clear loser: in its simulation of 100 contending clients, the jittered strategies completed the work with over 50% fewer calls.

Jitter breaks the synchronization by randomizing each wait. The three standard variants differ in how much randomness they add:

- **Full jitter**: `sleep = uniform(0, min(cap, base * 2**retry))`. Every wait is redrawn from scratch. This spreads load the most aggressively and is what the AWS SDKs use.
- **Equal jitter**: `sleep = capped / 2 + uniform(0, capped / 2)`. Keeps half the backoff deterministic, so waits stay closer to the exponential schedule while still decorrelating clients.
- **Decorrelated jitter**: `sleep = uniform(base, previous_sleep * 3)`, capped. Each wait depends on the previous one, which converges quickly without any shared schedule.

This article uses full jitter, matching the AWS SDK formula `random(0, 1) * min(cap, base * 2**retry)`, where `retry` is 0 for the wait before the first retry. (On the AWS SDK reference page, this 2026 retry behavior is described behind the `AWS_NEW_RETRIES_2026=true` flag; check the page for the current default before assuming your SDK uses it.)

To see what jitter buys, I ran a seeded simulation: 24 clients fail at t=0 and retry three times with base 1 s and cap 8 s, once with the full backoff and once with full jitter. The figure groups every retry attempt into 250 ms buckets across all three retry waves, so synchronized attempts from different waves stack into the same column.

![Two timelines of retry attempts. Without jitter the attempts form tall synchronized columns; with full jitter they spread thinly across time, under an illustrative capacity line.](jitter-lanes.svg "Seeded simulation (seed 7): 24 clients, 3 retries, base 1 s, cap 8 s. The busiest 250 ms bucket holds 24 attempts without jitter and 11 with full jitter."){: .figure}

The busiest 250 ms bucket holds 24 attempts without jitter and 11 with full jitter at seed 7 (11 at seeds 42 and 123, 10 at seed 2026). These are simulation measurements, not production capacity numbers: the point is the shape, not the values. Without jitter the attempts arrive as three synchronized columns; with jitter they spread across the whole window. The dashed capacity line is illustrative, but the dynamic is real: synchronized retries concentrate load exactly when the dependency is weakest, right after it recovers.

## Classify before you retry

Not every failure deserves a retry. A timeout might succeed on the next attempt; a malformed request will fail forever, and retrying it burns quota and fills logs. A `429` means "slow down," which pairs with a longer base delay, not the standard one. And a retried charge or a retried email send is not a performance problem, it is a correctness disaster.

The AWS SDK retry documentation classifies by error code first and HTTP status second, and the code lists are worth copying: a `400` with code `RequestTimeout` is transient, while a `400` with code `ValidationException` is permanent. Status-only classification gets both of these wrong. The classifier below encodes that priority: listed transient and throttling codes win, listed non-retryable codes like `ValidationException` win even over a 5xx status, and a code the documentation does not recognize falls back to the status rules, so a `503` with an unknown code is still transient. Without a recognized code, `408` and `500`/`502`/`503`/`504` are transient, `429` is throttling, and ordinary client errors (`400`, `404`, and friends) are permanent. One conservative rule stays absolute: a failure the classifier does not recognize at all is permanent. Never retry what you do not understand; an unknown failure retried in a loop is how a deploy bug becomes a self-inflicted DDoS.

```python
class TransientError(Exception):
    """A failure that may succeed if retried: timeouts, 5xx, dropped connections."""


class PermanentError(Exception):
    """A failure retrying cannot fix: bad requests, auth failures, missing data."""


class ServiceError(Exception):
    """A service failure carrying an HTTP status and/or a service error code.

    The error code wins over the status: ``400`` with code ``RequestTimeout``
    is transient, while ``400`` with code ``ValidationException`` is permanent.

    ``retry_after`` carries a server-directed wait in seconds: convert
    ``x-amz-retry-after`` (milliseconds) or the HTTP ``Retry-After`` header
    (seconds or an HTTP-date) to seconds before constructing the error.
    """

    def __init__(self, message: str = "", *, status: int | None = None,
                 code: str | None = None,
                 retry_after: float | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.retry_after = retry_after

    def __str__(self) -> str:
        bits = []
        if self.status is not None:
            bits.append(f"status={self.status}")
        if self.code is not None:
            bits.append(f"code={self.code}")
        if self.retry_after is not None:
            bits.append(f"retry_after={self.retry_after}s")
        detail = " ".join(bits)
        base = super().__str__()
        if detail and base:
            return f"{base} ({detail})"
        return detail or base or "ServiceError"


class RetryExhausted(Exception):
    """Raised when no further attempt will be made.

    ``reason`` is one of ``"permanent"``, ``"max_attempts"``, ``"budget"``,
    ``"deadline"`` or ``"not_idempotent"``; ``last_exc`` is the most recent
    failure, if any.
    """

    def __init__(self, reason: str, last_exc: BaseException | None = None) -> None:
        super().__init__(f"gave up: {reason}")
        self.reason = reason
        self.last_exc = last_exc


# Error codes taken from the AWS SDK retry documentation: codes that mark a
# failure transient, throttling, or non-retryable even when the HTTP status
# says otherwise. A code the documentation does not list falls back to the
# HTTP status rules in classify().
_TRANSIENT_CODES = frozenset({
    "RequestTimeout",
    "RequestTimeoutException",
    "InternalError",
    "IDPCommunicationError",
})

_THROTTLING_CODES = frozenset({
    "Throttling",
    "ThrottlingException",
    "ThrottledException",
    "RequestThrottled",
    "RequestThrottledException",
    "TooManyRequestsException",
    "ProvisionedThroughputExceededException",
    "TransactionInProgressException",
    "RequestLimitExceeded",
    "SlowDown",
    "BandwidthLimitExceeded",
    "PriorRequestNotComplete",
    "LimitExceededException",
    "EC2ThrottledException",
})

# Non-retryable codes named by the AWS SDK retry documentation. A listed
# code wins over the status: ValidationException on a 503 is still permanent.
_PERMANENT_CODES = frozenset({
    "AccessDeniedException",
    "ValidationException",
    "ResourceNotFoundException",
})

# Statuses the AWS SDK retry documentation treats as transient when no
# recognized error code is present.
_TRANSIENT_STATUSES = frozenset({500, 502, 503, 504})


def classify(exc: BaseException) -> str:
    """Classify a failure as ``"transient"``, ``"throttling"`` or ``"permanent"``.

    Rules, in order:

    1. Explicit markers win: :class:`TransientError` is transient,
       :class:`PermanentError` is permanent.
    2. Dropped connections and timeouts are transient; the network, not the
       request, failed.
    3. For :class:`ServiceError`, the error code wins over the HTTP status.
       A ``400`` with code ``RequestTimeout`` is transient; a ``400`` with
       code ``ValidationException`` is permanent. A code the documentation
       does not list falls back to the status rules, so a ``503`` with an
       unrecognized code is still transient.
    4. Without a recognized code, ``408`` and ``429`` are
       transient/throttling, ``500``/``502``/``503``/``504`` are transient,
       and every other status is permanent. Ordinary client errors
       (``400``, ``404``, ...) are not retried.
    5. Anything unrecognized is permanent: never retry what you do not
       understand.
    """
    if isinstance(exc, TransientError):
        return "transient"
    if isinstance(exc, PermanentError):
        return "permanent"
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return "transient"
    if isinstance(exc, ServiceError):
        if exc.code in _THROTTLING_CODES:
            return "throttling"
        if exc.code in _TRANSIENT_CODES:
            return "transient"
        if exc.code in _PERMANENT_CODES:
            return "permanent"
        if exc.status is not None:
            if exc.status == 429:
                return "throttling"
            if exc.status == 408 or exc.status in _TRANSIENT_STATUSES:
                return "transient"
            return "permanent"
    return "permanent"
```

The idempotency gate belongs with classification because it answers the same question: is repeating this call safe? A retried non-idempotent operation can execute its side effect twice. The helper therefore never retries a non-idempotent operation unless the caller supplies an idempotency key, which moves the deduplication responsibility to the receiver, the same contract [idempotent webhook handlers](/posts/idempotent-operations-in-distributed-systems-a-practical-guide/) rely on. If you cannot make the operation idempotent and you have no key, the call runs exactly once and is never retried: a failure raises `RetryExhausted` with reason `"not_idempotent"` instead of risking a second execution.

## Honor server-directed delays

Sometimes the service tells you exactly when to come back. AWS services may send an `x-amz-retry-after` header with error responses, carrying a delay in milliseconds; the AWS SDK retry documentation says the SDK then "uses the server-specified delay, clamped to a minimum of the computed backoff delay and a maximum of the computed backoff delay plus 5,000 ms," adding that it "does not apply jitter to this value, because the service is expected to jitter it." HTTP has the same idea in the standard `Retry-After` header, whose value is either a delay in seconds or an HTTP-date (RFC 9110, section 10.2.3).

The helper models this as `retry_after` on `ServiceError`, in seconds; convert milliseconds or an HTTP-date to seconds when constructing the error. When a failure carries one, the wait becomes the server's delay clamped to between the computed backoff and the computed backoff plus five seconds, matching the AWS SDK. The clamp matters in both directions: never shorter than your own backoff, so a buggy or hostile header cannot turn your client into a hot loop, and never more than five seconds longer, so a stale hint cannot park the operation. The wait must still fit inside the total deadline, so the server hint can never push the operation past its own budget of time.

## Bound the total cost

Two more gates keep retries from becoming a denial of service against your own dependency: a shared retry budget and a total deadline.

The budget is a token bucket shared by every caller of the dependency. Each retry consumes one token; tokens refill continuously with elapsed time up to a capacity. When the bucket is empty, callers fail fast instead of retrying. This is what stops one client's retry loop from overwhelming a dependency that is already struggling. Note the deliberate difference from the AWS SDK's model: the SDK's standard-mode quota bucket is replenished by successful requests, while this bucket refills only with time and successes never add tokens. Time-based refill bounds the retry rate even when every attempt is failing, which is exactly the situation a budget exists for. The bucket is thread-safe, so one instance can share it across threads.

```python
class TokenBucket:
    """A continuously refilling retry budget, safe to share across threads.

    Each retry consumes one token. Tokens refill with elapsed time at
    ``refill_per_second``, up to ``capacity``. Successes do not add tokens;
    only time does. When no token is available the caller must fail fast
    instead of retrying, which is what keeps one client's retries from
    becoming a denial of service against a struggling dependency.
    """

    def __init__(self, capacity: float, refill_per_second: float,
                 clock: Callable[[], float] = time.monotonic) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_per_second < 0:
            raise ValueError("refill_per_second must not be negative")
        self._capacity = float(capacity)
        self._rate = float(refill_per_second)
        self._clock = clock
        self._tokens = float(capacity)
        self._updated = clock()
        self._lock = threading.Lock()

    def take(self) -> bool:
        """Consume one token for a retry; return False when the budget is empty."""
        with self._lock:
            now = self._clock()
            elapsed = now - self._updated
            if elapsed > 0:
                self._tokens = min(
                    self._capacity, self._tokens + elapsed * self._rate)
                self._updated = now
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return True
            return False

    def available(self) -> float:
        """Tokens currently available, after refilling for elapsed time."""
        with self._lock:
            now = self._clock()
            elapsed = now - self._updated
            if elapsed > 0:
                self._tokens = min(
                    self._capacity, self._tokens + elapsed * self._rate)
                self._updated = now
            return self._tokens
```

The deadline bounds the whole operation, not just one wait. Each attempt receives the seconds remaining until the deadline and should use that value as its own I/O timeout, for example the `timeout` argument of an HTTP client. One honest limitation: arbitrary synchronous Python code cannot be forcibly interrupted, so the helper bounds its own scheduling, not the callee's code. An attempt that ignores the remaining time it was given can still run past the deadline; what the helper guarantees is that it will never *start* a wait that does not fit inside the deadline.

Gate order matters. The loop checks the deadline *before* taking a budget token, so a retry that never runs never spends budget. A token is consumed only when the wait is actually going to happen.

![Flowchart: a non-idempotent call without a key runs once and is never retried; otherwise each failed attempt passes five gates, idempotent or keyed, transient or throttling, attempts left, wait fits in deadline, budget token; failing any gate raises RetryExhausted, passing all five sleeps and retries.](retry-decision.svg "Five gates before any wait. A retry happens only when the operation is safe to repeat, the error is transient, attempts remain, the wait fits in the deadline, and the budget has a token."){: .figure}

```python
def with_retries(
    fn: Callable[[float | None], object],
    *,
    max_attempts: int = 4,
    base_delay: float = 0.05,
    throttling_base_delay: float = 1.0,
    max_delay: float = 20.0,
    total_timeout: float | None = None,
    budget: TokenBucket | None = None,
    idempotent: bool = True,
    idempotency_key: str | None = None,
    rng: random.Random | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> object:
    """Run ``fn`` with a safe retry policy and return its result.

    ``fn`` receives the seconds remaining until the deadline (``None`` when
    no deadline is set) and should use it as its own timeout. Attempts are
    numbered from 1; retries happen only when ``fn`` raises a transient or
    throttling failure (see :func:`classify`).

    When the operation is not idempotent and no idempotency key is
    supplied, it is not safe to repeat: ``fn`` runs exactly once and is
    never retried. A failure then raises :class:`RetryExhausted` with reason
    ``"not_idempotent"``.

    The loop stops, raising :class:`RetryExhausted`, when the failure is
    permanent, ``max_attempts`` is reached, the budget has no token left, or
    the next wait would not fit inside ``total_timeout``. A budget token is
    consumed only when a wait is actually going to happen: a retry that never
    runs never spends budget.

    A failure carrying ``retry_after``, a server-directed wait in seconds
    (from ``x-amz-retry-after`` or the HTTP ``Retry-After`` header), takes
    precedence over the jittered backoff: the wait becomes the server's
    delay, clamped to between the computed backoff and the computed backoff
    plus five seconds, matching the AWS SDK behavior. The service is expected
    to jitter its own value, so no extra jitter is applied; the wait must
    still fit inside ``total_timeout``.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    if rng is None:
        rng = random.Random()
    deadline = clock() + total_timeout if total_timeout is not None else None

    if not idempotent and not idempotency_key:
        # Not safe to repeat, and no key for the receiver to deduplicate by:
        # run exactly once, never retry. A failure raises RetryExhausted
        # with reason "not_idempotent" rather than risking a second
        # execution.
        remaining = deadline - clock() if deadline is not None else None
        if remaining is not None and remaining <= 0:
            raise RetryExhausted("deadline") from None
        try:
            return fn(remaining)
        except Exception as exc:  # noqa: BLE001 - policy applies to any failure
            raise RetryExhausted("not_idempotent", exc) from exc

    last_exc: BaseException | None = None
    for attempt in range(1, max_attempts + 1):
        remaining = deadline - clock() if deadline is not None else None
        if remaining is not None and remaining <= 0:
            raise RetryExhausted("deadline", last_exc) from last_exc
        try:
            return fn(remaining)
        except Exception as exc:  # noqa: BLE001 - policy applies to any failure
            kind = classify(exc)
            if kind == "permanent":
                raise RetryExhausted("permanent", exc) from exc
            last_exc = exc
            if attempt >= max_attempts:
                break
            base = throttling_base_delay if kind == "throttling" else base_delay
            delay = _full_jitter_delay(attempt - 1, base, max_delay, rng)
            if isinstance(exc, ServiceError) and exc.retry_after is not None \
                    and exc.retry_after > 0:
                # Server-directed timing: use the server's wait, clamped to a
                # minimum of the computed backoff and a maximum of the
                # computed backoff plus five seconds, as the AWS SDK does.
                delay = min(max(exc.retry_after, delay), delay + 5.0)
            if remaining is not None:
                # Re-read the clock: the failed attempt consumed some of the
                # deadline, so the wait must fit in what is left, not what
                # was left before the attempt.
                remaining = deadline - clock()
                if delay >= remaining:
                    raise RetryExhausted("deadline", exc) from exc
            if budget is not None and not budget.take():
                raise RetryExhausted("budget", exc) from exc
            sleep(delay)
    raise RetryExhausted("max_attempts", last_exc) from last_exc
```

The delay defaults mirror the AWS SDK's: a 50 ms base for transient failures, a 1.0 s base for throttling, and a 20 s cap. The attempt default is four total tries, one initial plus three retries, matching the SRE book's per-layer example; the SDK itself defaults to three. Throttling gets its own slower base because a `429` is the dependency asking for less load, and answering it with the same aggressive schedule that caused the throttle is how clients get themselves blocked.

## Failure modes

| Naive behavior | What you see | Cause | Fix |
| :--- | :--- | :--- | :--- |
| Retries at the client, the sidecar, and the backend | Load multiplies on every blip; dashboards show attempt counts far above request counts | Each layer adds its own attempts | Designate one retrying layer per call chain; inner layers fail fast |
| Fixed or pure exponential backoff, no jitter | Recovery traffic arrives in synchronized waves; the dependency tips over again right after recovering | Identical sleep schedules from a common failure time | Full jitter: `uniform(0, min(cap, base * 2**n))` |
| Retrying every 4xx | Quota burned on requests that can never succeed | Status-only classification | Code-first classification; unrecognized codes fall back to status, unrecognized failures are permanent |
| Retrying a charge or a send without a key | Double charges, duplicate side effects | Non-idempotent operation repeated | Run exactly once, never retry; failure raises with reason `not_idempotent` |
| Ignoring the server's retry-after hint | Retries land while the service is still shedding load | Server-directed wait carried but never applied | Wait the server's delay, clamped to `[backoff, backoff + 5 s]`, inside the deadline |
| No total deadline | A slow dependency holds caller threads for minutes; pools exhaust | Waits bounded individually but not in total | Pass the remaining time to each attempt; never start a wait that does not fit |
| No retry budget | One client's retries become a DoS against a struggling dependency | Aggregate retries unbounded | Shared token bucket; fail fast when empty |
| Budget consumed before the deadline check | Budget leaks on retries that never run | Wrong gate order | Check the deadline first; spend the token only on a retry that will run |

## Proving it works

The test suite runs 29 tests in about 0.02 seconds on Python 3.12.3:

```text
python3 -W error::DeprecationWarning -m unittest test_retry -v
```

A fake clock stands in for `time.monotonic` and `time.sleep`, so every timing assertion is deterministic; a seeded `random.Random` makes the jitter schedule reproducible. The tests that matter most:

- **Code wins over status.** `400` with code `RequestTimeout` is retried; `400` with code `ValidationException` is not; a `503` with a throttling code classifies as throttling, not transient. A listed non-retryable code wins even over a 5xx status, while an unrecognized code falls back to the status rules. `501` without a code is permanent.
- **Budget is never spent on a phantom retry.** With a one-token bucket and a deadline the longest possible wait cannot fit, the loop raises `RetryExhausted("deadline")` and the token is still there afterward.
- **Non-idempotent means one attempt, never a retry.** A non-idempotent operation without a key fails with reason `not_idempotent` after exactly one call, and the empty-string key behaves the same way.
- **Server hints are honored, clamped, and deadline-bound.** A 2 s `retry_after` overrides the shorter backoff; a 10 ms hint stays below it; a 60 s hint is capped at backoff + 5 s; and a hint that does not fit the deadline raises `deadline`.
- **The deadline bounds helper-controlled time.** Attempts receive non-increasing remaining times, and sleeps plus cooperative work stay inside the deadline:

```python
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
```

- **Thread safety under contention.** 200 threads race for 50 tokens; exactly 50 win.
- **Backoff shape.** A stub RNG returning the top of the range exposes the raw schedule: `[0.5, 1.0, 2.0, 4.0]` for base 0.5, and every delay stays under the cap.
- **Full jitter is deterministic given a seed.** Two runs with the same seed produce identical wait sequences, each within `[0, cap]`.

The simulation behind the jitter figure ships as `retry_sim.py` in the article folder; rerun it with any seed to reproduce the peak numbers quoted above.

## Operating it

Retries are invisible load until they are measured. Export four metrics per operation:

- `retry_attempts_total{operation, outcome}` where outcome is `success` or `giveup`.
- `retry_giveups_total{operation, reason}` where reason is one of `permanent`, `max_attempts`, `budget`, `deadline`, or `not_idempotent`, matching the `RetryExhausted` reasons.
- `retry_budget_available` as a gauge on the shared bucket.
- `retry_backoff_seconds` as a histogram of actual waits.

Alert on the giveup ratio by reason, not on retries in the abstract. Retries happening is normal; giveups clustering on one reason is the signal:

- `reason="budget"` giveups sustained above zero mean the dependency is shedding your retries. Investigate the dependency before raising the budget; raising it during an outage just buys a bigger thundering herd.
- `reason="deadline"` climbing means the total timeout is too tight for current latency, or the dependency's p99 grew. Check whether the timeout or the dependency moved.
- `reason="permanent"` spiking after a deploy means a client bug is now failing fast on every call. Roll back the client, not the retry policy.
- `reason="not_idempotent"` appearing at all means callers are sending non-idempotent operations without keys. Fix the callers; the helper is already refusing to retry them.
- `retry_budget_available` near zero for minutes means a retry storm is in progress somewhere upstream.

Example queries (Prometheus):

```promql
sum by (reason) (rate(retry_giveups_total[5m]))
retry_budget_available < 1
histogram_quantile(0.99, sum by (le) (rate(retry_backoff_seconds_bucket[5m])))
```

Size the bucket from the dependency's documented rate limit, not from your client's wishes: capacity is the burst you can afford, and the refill rate is the sustained retry rate the dependency can absorb on top of normal traffic. A starting point, and this is my own heuristic rather than a sourced number, is a refill rate of 5-10% of the dependency's per-client quota; adjust from the `budget` giveup rate in production. Two caveats: the bucket is process-local, so each instance of your service gets its own, and a restart refills it to capacity. Size capacity so that a simultaneous restart of the whole fleet, every bucket full at once, is still a burst the dependency survives. If it is not, share one bucket per fleet through Redis instead of one per process.

## Trade-offs and alternatives

Do not retry a non-idempotent operation when you have no key; run it once instead. Do not retry when the caller's latency budget is better spent failing fast, as with user-facing requests where a quick error beats a slow one; when the dependency is hard down rather than flapping, because retries add load to a system that needs quiet to recover; or when the work can wait, in which case enqueue it and process it asynchronously instead of holding a caller thread.

Three alternatives, each winning under a different condition:

- **Circuit breaker.** Wins when the dependency stays down for minutes. A breaker fails fast without the per-call wait, and half-opens to probe recovery. See [the Resilience4j circuit breaker guide](/posts/boosting-microservice-resilience-implementing-circuit-breaker-pattern-with-resilience4j/) for the mechanics. In practice, compose them: the breaker in front, this retry policy behind it for the transient blips the breaker lets through.
- **Hedged requests.** Wins when the tail latency matters more than the extra load, typically idempotent reads against a dependency with spare capacity. Send a second request after a delay instead of waiting for the first to fail.
- **Fail fast plus an async queue.** Wins for deferrable writes. The [transactional outbox](/posts/transactional-outbox-reliable-events-without-dual-writes/) is the durable version of this: accept the write, deliver it later, retry the delivery with no caller waiting.

Recommendation: use this helper for transient faults at exactly one layer, with a budget and a deadline, and put a circuit breaker around it when the dependency can stay down longer than your deadline. Retries handle blips; breakers handle outages; neither handles a non-idempotent operation, which is what the idempotency gate is for.

## Checklist

1. Exactly one layer in the call chain retries; inner layers fail fast with tight timeouts.
2. Backoff is exponential, capped, and fully jittered; the cap is below the caller's patience.
3. Error classification is code-first with status fallback; ordinary 4xx and unrecognized failures are permanent.
4. A non-idempotent operation without a key runs exactly once and is never retried; with a key it follows the normal policy.
5. A shared budget bounds aggregate retries, and tokens are spent only on retries that run.
6. Every attempt receives the remaining deadline and applies it to its I/O timeout.
7. Giveups are counted by reason (`permanent`, `max_attempts`, `budget`, `deadline`, `not_idempotent`) and alerted on.

## References

- [Timeouts, retries, and backoff with jitter](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter) (AWS Builder Center): retry at one layer, capped backoff with jitter, idempotency, and token-bucket throttling.
- [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter) (AWS Architecture Blog): why unjittered backoff loses, the full/equal/decorrelated jitter variants, and the 100-client simulation results.
- [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) (Google SRE book): the 4 x 4 x 4 = 64 attempt amplification, one retry layer, retry budgets, and deadline propagation.
- [Retry behavior](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html) (AWS SDKs and Tools Reference): the full-jitter formula, error-code-first classification, and the throttling base delay. The described 2026 behavior requires `AWS_NEW_RETRIES_2026=true`.
- [RFC 9110, section 10.2.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-10.2.3) (IETF): the `Retry-After` header field, an HTTP-date or a delay in seconds, telling the client how long to wait before a follow-up request.
