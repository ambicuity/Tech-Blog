"""Tests for the Redis distributed lock. Skipped unless redis + fakeredis
are installed: ``pip install redis fakeredis``.

Run: ``python3 -m unittest test_redis_lock -v`` from this folder.
"""

import time
import unittest

try:
    import fakeredis
    import redis  # noqa: F401 - imported to prove redis-py is present
except ImportError:
    fakeredis = None

from redis_lock import LockNotAcquired, RedisLock


def _supports_eval() -> bool:
    """fakeredis runs Lua only when lupa is installed; probe instead of assuming."""
    if fakeredis is None:
        return False
    try:
        fakeredis.FakeRedis(decode_responses=True).eval("return 1", 0)
        return True
    except Exception:  # noqa: BLE001 - any failure means "no Lua here"
        return False


@unittest.skipUnless(fakeredis is not None, "redis + fakeredis not installed")
@unittest.skipUnless(_supports_eval(), "fakeredis needs lupa for Lua scripts")
class TestRedisLock(unittest.TestCase):
    def setUp(self):
        self.client = fakeredis.FakeRedis(decode_responses=True)

    def test_second_acquire_fails_while_held(self):
        first = RedisLock(self.client, "lock:product:42")
        second = RedisLock(self.client, "lock:product:42")
        self.assertTrue(first.acquire())
        self.assertFalse(second.acquire())
        self.assertTrue(first.release())

    def test_release_only_by_owner(self):
        first = RedisLock(self.client, "lock:product:42")
        impostor = RedisLock(self.client, "lock:product:42")
        self.assertTrue(first.acquire())
        self.assertFalse(impostor.release())
        self.assertEqual(self.client.get("lock:product:42"), first.token)
        self.assertTrue(first.release())
        self.assertIsNone(self.client.get("lock:product:42"))

    def test_context_manager_releases_on_exit(self):
        with RedisLock(self.client, "lock:product:42"):
            self.assertIsNotNone(self.client.get("lock:product:42"))
        self.assertIsNone(self.client.get("lock:product:42"))

    def test_context_manager_raises_when_held(self):
        with RedisLock(self.client, "lock:product:42"):
            with self.assertRaises(LockNotAcquired):
                with RedisLock(self.client, "lock:product:42"):
                    pass

    def test_lock_expires_so_a_crash_cannot_wedge_forever(self):
        lock = RedisLock(self.client, "lock:product:42", px_ms=50)
        self.assertTrue(lock.acquire())
        time.sleep(0.15)
        retry = RedisLock(self.client, "lock:product:42", px_ms=50)
        self.assertTrue(retry.acquire())
        # The original holder's release must not delete the new holder's lock.
        self.assertFalse(lock.release())
        self.assertIsNotNone(self.client.get("lock:product:42"))


if __name__ == "__main__":
    unittest.main()
