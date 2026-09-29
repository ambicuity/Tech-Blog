"""Retry helper: capped exponential backoff, full jitter, retry budget, deadline.

Pinned runtime: Python 3.12, standard library only.

What this module guarantees:

- every wait between attempts is exponentially backed off, capped, and fully
  jittered;
- retries stop when the error is permanent, the attempt limit is hit, the
  retry budget is empty, or the total deadline no longer fits another wait;
- a non-idempotent operation is never retried unless the caller supplies an
  idempotency key.

What it cannot do: interrupt a running attempt. Each attempt receives the
seconds remaining until the deadline, and a cooperative operation should use
that value as its own timeout (for example, the ``timeout`` argument of an
HTTP client). An operation that ignores the value it is given can still run
past the deadline; the helper bounds its own scheduling, not the callee's code.
"""

from __future__ import annotations

import random
import threading
import time
from collections.abc import Callable


# [block errors]
class TransientError(Exception):
    """A failure that may succeed if retried: timeouts, 5xx, dropped connections."""


class PermanentError(Exception):
    """A failure retrying cannot fix: bad requests, auth failures, missing data."""


class ServiceError(Exception):
    """A service failure carrying an HTTP status and/or a service error code.

    The error code wins over the status: ``400`` with code ``RequestTimeout``
    is transient, while ``400`` with code ``ValidationException`` is permanent.
    """

    def __init__(self, message: str = "", *, status: int | None = None,
                 code: str | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.code = code

    def __str__(self) -> str:
        bits = []
        if self.status is not None:
            bits.append(f"status={self.status}")
        if self.code is not None:
            bits.append(f"code={self.code}")
        detail = " ".join(bits)
        base = super().__str__()
        if detail and base:
            return f"{base} ({detail})"
        return detail or base or "ServiceError"


class NonIdempotentError(ValueError):
    """Raised when asked to retry an operation that is not safe to repeat."""


class RetryExhausted(Exception):
    """Raised when no further attempt will be made.

    ``reason`` is one of ``"permanent"``, ``"max_attempts"``, ``"budget"`` or
    ``"deadline"``; ``last_exc`` is the most recent failure, if any.
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
# [/block errors]


# [block bucket]
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
# [/block bucket]


def _full_jitter_delay(retry_index: int, base_delay: float, max_delay: float,
                       rng: random.Random) -> float:
    """Capped exponential backoff with full jitter for one wait.

    ``retry_index`` is 0 for the wait before the first retry, matching the
    AWS SDK formula ``random(0, 1) * min(cap, base * 2**retry)``.
    """
    capped = min(max_delay, base_delay * (2 ** retry_index))
    return rng.uniform(0, capped)


# [block retry]
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

    The loop stops, raising :class:`RetryExhausted`, when the failure is
    permanent, ``max_attempts`` is reached, the budget has no token left, or
    the next wait would not fit inside ``total_timeout``. A budget token is
    consumed only when a wait is actually going to happen: a retry that never
    runs never spends budget.
    """
    if not idempotent and not idempotency_key:
        raise NonIdempotentError(
            "refusing to retry a non-idempotent operation without an "
            "idempotency key: a repeated side effect could execute twice")
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    if rng is None:
        rng = random.Random()
    deadline = clock() + total_timeout if total_timeout is not None else None

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
# [/block retry]
