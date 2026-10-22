"""Proving tests for config_client.py: every guarantee the article claims,
including a replay of the 2026-09-28 Firebase GA4F incident shape
(server removes a flag the client still references).

Run: python3 test_config_client.py
Python 3.12, stdlib only.
"""

import json
import os
import tempfile
import unittest

from config_client import (
    ConfigClient,
    FetchResult,
    FlagSpec,
    _cohort_bucket,
)

SCHEMA = [
    FlagSpec("new_checkout", "bool", False),
    FlagSpec("timeout_ms", "int", 3000),
    FlagSpec("banner_text", "str", "hello"),
    FlagSpec("sample_rate", "float", 0.1),
]


def fresh_client(schema=SCHEMA, client_id="client-1", **kw):
    d = tempfile.mkdtemp(prefix="cfg-test-")
    return ConfigClient(schema, client_id, os.path.join(d, "cache.json"), **kw), d


def full_payload():
    return json.dumps(
        {
            "new_checkout": True,
            "timeout_ms": 5000,
            "banner_text": "hi",
            "sample_rate": 0.5,
        }
    ).encode()


class TestHappyPath(unittest.TestCase):
    def test_valid_payload_applies_all(self):
        c, _ = fresh_client()
        r = c.fetch(full_payload())
        self.assertTrue(r.payload_ok)
        self.assertEqual(c.get("new_checkout"), True)
        self.assertEqual(c.get("timeout_ms"), 5000)
        self.assertEqual(c.get("banner_text"), "hi")
        self.assertEqual(c.get("sample_rate"), 0.5)
        self.assertEqual(len(r.applied), 4)
        self.assertEqual(r.ignored, [])

    def test_empty_payload_keeps_everything(self):
        c, _ = fresh_client()
        r = c.fetch(b"{}")
        self.assertTrue(r.payload_ok)
        self.assertEqual(c.get("timeout_ms"), 3000)
        self.assertEqual(len(r.kept_cached), 4)


class TestNilNameIncident(unittest.TestCase):
    """The 2026-09-28 shape: the server sent a flag whose name was nil.
    On the wire that is an empty or non-string key. The client must not crash."""

    def test_empty_key_name_is_ignored_not_fatal(self):
        c, _ = fresh_client()
        r = c.fetch(json.dumps({"": True, "new_checkout": True}).encode())
        self.assertTrue(r.payload_ok)
        self.assertEqual(c.get("new_checkout"), True)  # good flags still apply

    def test_coerced_keys_become_unknown_flags(self):
        # JSON object keys are always strings, so a None key arrives as the
        # string "null": the true nil-name wire shape is the empty key (tested
        # above). The client must still not crash on coerced keys; it treats
        # them as unknown flags.
        c, _ = fresh_client()
        d = {"new_checkout": True}
        d[None] = True
        r = c.fetch(json.dumps(d).encode())
        self.assertTrue(r.payload_ok)
        self.assertEqual(c.get("new_checkout"), True)
        self.assertEqual(c.metrics["unknown_flags_total"], 1)

    def test_server_removed_flag_keeps_cached_value(self):
        """Replay: the server removed a flag the client still references.
        The GA4F SDK dereferenced the missing flag and crashed; this client
        keeps its cached value and carries on."""
        c, _ = fresh_client()
        c.fetch(full_payload())  # learn good values first
        self.assertEqual(c.get("timeout_ms"), 5000)
        # server-side "cleanup": the flag disappears from the payload
        removed = json.dumps(
            {"new_checkout": True, "banner_text": "hi", "sample_rate": 0.5}
        ).encode()
        r = c.fetch(removed)  # must not raise
        self.assertTrue(r.payload_ok)
        self.assertEqual(c.get("timeout_ms"), 5000)  # cached value kept
        self.assertIn("timeout_ms", r.kept_cached)


class TestPerFlagIsolation(unittest.TestCase):
    def test_one_bad_flag_does_not_poison_others(self):
        c, _ = fresh_client()
        r = c.fetch(
            json.dumps(
                {"new_checkout": True, "timeout_ms": "fast", "banner_text": "hi"}
            ).encode()
        )
        self.assertTrue(r.payload_ok)
        self.assertEqual(c.get("new_checkout"), True)
        self.assertEqual(c.get("timeout_ms"), 3000)  # bad value ignored
        self.assertEqual(c.get("banner_text"), "hi")
        ignored_names = [n for n, _ in r.ignored]
        self.assertIn("timeout_ms", ignored_names)

    def test_bool_is_not_an_int(self):
        c, _ = fresh_client()
        r = c.fetch(json.dumps({"timeout_ms": True}).encode())
        self.assertEqual(c.get("timeout_ms"), 3000)
        self.assertTrue(any(n == "timeout_ms" for n, _ in r.ignored))

    def test_unknown_flag_ignored_for_forward_compat(self):
        c, _ = fresh_client()
        r = c.fetch(json.dumps({"future_flag_v2": 1, "new_checkout": True}).encode())
        self.assertTrue(r.payload_ok)
        self.assertEqual(c.get("new_checkout"), True)
        self.assertEqual(c.metrics["unknown_flags_total"], 1)

    def test_malformed_json_rejected_whole_config_unchanged(self):
        c, _ = fresh_client()
        c.fetch(full_payload())
        r = c.fetch(b"{not json")
        self.assertFalse(r.payload_ok)
        self.assertEqual(c.get("new_checkout"), True)  # previous good config kept
        self.assertEqual(c.metrics["payload_rejected_total"], 1)

    def test_non_dict_payload_rejected(self):
        c, _ = fresh_client()
        r = c.fetch(json.dumps([1, 2, 3]).encode())
        self.assertFalse(r.payload_ok)
        r = c.fetch(None)
        self.assertFalse(r.payload_ok)


class TestRolloutCohorts(unittest.TestCase):
    def test_cohort_is_deterministic_per_client(self):
        b1 = _cohort_bucket("client-9", "new_checkout")
        b2 = _cohort_bucket("client-9", "new_checkout")
        self.assertEqual(b1, b2)

    def test_rollout_zero_never_applies(self):
        schema = [FlagSpec("flag", "bool", False, rollout_pct=0.0)]
        c, _ = fresh_client(schema=schema, client_id="any")
        r = c.fetch(json.dumps({"flag": True}).encode())
        self.assertEqual(c.get("flag"), False)
        self.assertIn("flag", r.kept_cached)

    def test_rollout_hundred_always_applies(self):
        schema = [FlagSpec("flag", "bool", False, rollout_pct=100.0)]
        c, _ = fresh_client(schema=schema, client_id="any")
        c.fetch(json.dumps({"flag": True}).encode())
        self.assertEqual(c.get("flag"), True)

    def test_partial_rollout_pins_stable_cohort(self):
        schema = [FlagSpec("flag", "bool", False, rollout_pct=50.0)]
        c1, _ = fresh_client(schema=schema, client_id="sticky")
        c2, _ = fresh_client(schema=schema, client_id="sticky")
        c1.fetch(json.dumps({"flag": True}).encode())
        c2.fetch(json.dumps({"flag": True}).encode())
        self.assertEqual(c1.get("flag"), c2.get("flag"))  # same cohort, same outcome


class TestDegradedMode(unittest.TestCase):
    def test_consecutive_bad_payloads_trip_degraded(self):
        c, _ = fresh_client(degraded_after=3)
        c.fetch(full_payload())
        for _ in range(3):
            c.fetch(b"garbage")
        self.assertTrue(c.metrics["degraded"])
        self.assertEqual(c.metrics["consecutive_bad_fetches"], 3)
        self.assertEqual(c.get("new_checkout"), True)  # cache is the source of truth

    def test_good_payload_clears_degraded(self):
        c, _ = fresh_client(degraded_after=2)
        c.fetch(b"garbage")
        c.fetch(b"garbage")
        self.assertTrue(c.metrics["degraded"])
        c.fetch(full_payload())
        self.assertFalse(c.metrics["degraded"])
        self.assertEqual(c.metrics["consecutive_bad_fetches"], 0)


class TestCacheDurability(unittest.TestCase):
    def test_cache_survives_restart(self):
        c, d = fresh_client()
        c.fetch(full_payload())
        path = c._cache_path
        c2 = ConfigClient(SCHEMA, "client-1", path)
        self.assertEqual(c2.get("timeout_ms"), 5000)
        self.assertEqual(c2.get("banner_text"), "hi")

    def test_corrupt_cache_starts_from_defaults(self):
        d = tempfile.mkdtemp(prefix="cfg-test-")
        path = os.path.join(d, "cache.json")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("{corrupt")
        c = ConfigClient(SCHEMA, "client-1", path)  # must not raise
        self.assertEqual(c.get("timeout_ms"), 3000)

    def test_metrics_are_scalars(self):
        c, _ = fresh_client()
        c.fetch(full_payload())
        c.fetch(b"bad")
        for name, value in c.metrics.items():
            self.assertIsInstance(value, (bool, int, float, str), name)


if __name__ == "__main__":
    unittest.main(verbosity=1)
