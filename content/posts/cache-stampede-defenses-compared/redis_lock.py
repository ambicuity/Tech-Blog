"""Distributed single-flight lock on Redis.

When the cache is shared across processes, the in-memory coalescing in
``cache.py`` is not enough: two processes can both miss the same key and
both load. The fix is the same idea one level out: a lock in Redis, held
only for the duration of the load.

Acquire is ``SET key token NX PX <timeout>``: set only if absent, with a
timeout so a crashed holder cannot wedge every other process forever.
Release must be atomic compare-and-delete, or a process could delete a
lock that already expired and now belongs to someone else. That is what
the Lua script does: it deletes only when the stored token is ours.

The token must be unique per holder (a random token per lock instance).
The timeout must be longer than the slowest legitimate load, or the lock
expires mid-load and a second process starts loading too. Pick the
timeout from measured load latency, not from a guess, and treat a lock
that keeps expiring as a signal that the loader is too slow, not as a
reason to remove the timeout.

Requires ``redis`` (redis-py 5.1+). Tested against fakeredis.
"""

from __future__ import annotations

import secrets

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
