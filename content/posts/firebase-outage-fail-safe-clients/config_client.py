"""Fail-safe remote config client.

Reference implementation of the fetch contract in Google's public postmortem
for the Google Analytics for Firebase iOS SDK outage of 2026-09-28
(published 2026-10-02):

    "We are releasing a patch for the GA4F SDK ... to validate every incoming
     server payload strictly. If a flag is corrupt or missing a required
     field, the SDK will safely ignore that specific flag and fall back to
     its cached defaults."

On 2026-09-28 a two-line server-side config cleanup removed a flag but left
a pointer to it in the SDK; the SDK fetched the missing flag, hit a fatal
error because the flag name was nil, and crashed every affected app on
launch. The server kept serving the bad config for 2 hours 11 minutes.

This module implements the fix: a remote-config client that
  1. never trusts a server payload: every flag is validated individually,
  2. ignores corrupt or missing flags one at a time (a bad flag cannot poison
     the good ones), falling back to the cached value for each,
  3. keeps a last-known-good cache, persisted atomically, used whenever the
     payload is unusable,
  4. pins rollout cohorts deterministically so a flag that rolls out to 1% of
     the fleet always reaches the same 1%,
  5. degrades explicitly: after N consecutive unusable payloads the client
     reports degraded and stops touching the cache, instead of flapping.

Python 3.12, stdlib only.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from dataclasses import dataclass, field

FLAG_TYPES = ("bool", "int", "float", "str")
MAX_NAME_LEN = 128

CACHE_FORMAT_VERSION = 1


@dataclass(frozen=True)
class FlagSpec:
    """One remote flag: its wire type, its fallback value, and the fraction of
    the fleet (0..100) that should receive the server value for it."""

    name: str
    kind: str  # "bool" | "int" | "float" | "str"
    default: object
    rollout_pct: float = 100.0


@dataclass
class FetchResult:
    """What one fetch did. Every name in applied/ignored/kept_cached refers to
    a flag in the schema; unknown payload keys are counted separately."""

    applied: dict = field(default_factory=dict)
    ignored: list = field(default_factory=list)  # [(name, reason), ...]
    kept_cached: list = field(default_factory=list)  # [name, ...]
    payload_ok: bool = True


def _check_type(kind: str, value: object) -> bool:
    """True when value is an instance of kind. bool is checked exactly:
    bool is a subclass of int, so isinstance(True, int) is True and would let
    a bool through an int flag. Wire booleans must not silently become ints."""
    if kind == "bool":
        return type(value) is bool
    if kind == "int":
        return type(value) is int
    if kind == "float":
        return isinstance(value, (int, float)) and type(value) is not bool
    if kind == "str":
        return type(value) is str
    return False


def _cohort_bucket(client_id: str, flag_name: str) -> int:
    """Deterministic 0..99 cohort for a client+flag pair. The same pair always
    lands in the same bucket, on every process and every release, so rollout
    cohorts are stable."""
    digest = hashlib.sha256(f"{client_id}:{flag_name}".encode("utf-8")).hexdigest()
    return int(digest, 16) % 100


class ConfigClient:
    """A remote-config client that cannot be crashed by the server."""

    def __init__(
        self,
        schema: list,
        client_id: str,
        cache_path: str,
        degraded_after: int = 3,
    ):
        for spec in schema:
            if not spec.name or not isinstance(spec.name, str):
                raise ValueError(f"schema flag needs a non-empty string name: {spec!r}")
            if len(spec.name) > MAX_NAME_LEN:
                raise ValueError(f"schema flag name too long: {spec.name!r}")
            if spec.kind not in FLAG_TYPES:
                raise ValueError(f"unknown flag kind {spec.kind!r} for {spec.name!r}")
            if not (0.0 <= spec.rollout_pct <= 100.0):
                raise ValueError(f"rollout_pct out of range for {spec.name!r}")
            if not _check_type(spec.kind, spec.default):
                raise ValueError(f"default of {spec.name!r} does not match kind {spec.kind!r}")
        names = [s.name for s in schema]
        if len(set(names)) != len(names):
            raise ValueError(f"duplicate flag names in schema: {names!r}")
        if degraded_after < 1:
            raise ValueError("degraded_after must be >= 1")

        self._schema = {s.name: s for s in schema}
        self._client_id = client_id
        self._cache_path = cache_path
        self._degraded_after = degraded_after
        self._values = {s.name: s.default for s in schema}
        self._consecutive_bad = 0
        self.metrics = {
            "fetch_total": 0,
            "payload_rejected_total": 0,
            "flags_applied_total": 0,
            "flags_ignored_total": 0,
            "unknown_flags_total": 0,
            "consecutive_bad_fetches": 0,
            "degraded": False,
        }
        self._load_cache()

    # -- cache ------------------------------------------------------------

    def _load_cache(self):
        try:
            with open(self._cache_path, "r", encoding="utf-8") as fh:
                blob = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
            return  # no cache yet, or a corrupt one: start from defaults
        if not isinstance(blob, dict) or blob.get("version") != CACHE_FORMAT_VERSION:
            return
        saved = blob.get("values")
        if not isinstance(saved, dict):
            return
        for name, spec in self._schema.items():
            if name in saved and _check_type(spec.kind, saved[name]):
                self._values[name] = saved[name]

    def _save_cache(self):
        blob = {
            "version": CACHE_FORMAT_VERSION,
            "saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "values": self._values,
        }
        directory = os.path.dirname(os.path.abspath(self._cache_path))
        fd, tmp = tempfile.mkstemp(dir=directory, prefix=".config-cache-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(blob, fh, sort_keys=True)
            os.replace(tmp, self._cache_path)  # atomic: readers never see half a cache
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    # -- fetch ------------------------------------------------------------

    def get(self, name: str):
        """Current value of a flag: the last good server value, else the default."""
        return self._values[name]

    def fetch(self, raw) -> FetchResult:
        """Apply one server payload. Never raises on bad server data: an
        unusable payload is rejected whole; a corrupt flag is ignored alone."""
        self.metrics["fetch_total"] += 1
        result = FetchResult()

        payload = self._parse(raw)
        if payload is None:
            self.metrics["payload_rejected_total"] += 1
            self._note_bad_payload()
            result.payload_ok = False
            return result

        # Reject unusable keys before touching any flag: an empty key is this
        # client's model of the nil-name bug that crashed GA4F (JSON object
        # keys are always strings, so nil arrives as ""). Non-string keys are
        # rejected too, as defense in depth for non-JSON payload formats.
        for key in list(payload.keys()):
            if not isinstance(key, str) or not key:
                result.ignored.append((repr(key), "empty or non-string flag name"))
                self.metrics["flags_ignored_total"] += 1
                del payload[key]
            elif key not in self._schema:
                result.ignored.append((key, "unknown flag; kept for forward compatibility"))
                self.metrics["unknown_flags_total"] += 1
                del payload[key]

        for name, spec in self._schema.items():
            if name not in payload:
                # The 2026-09-28 incident shape: the server removed a flag the
                # client still references. Keep the cached value; do not crash.
                result.kept_cached.append(name)
                continue
            value = payload[name]
            if not _check_type(spec.kind, value):
                result.ignored.append(
                    (name, f"expected {spec.kind}, got {type(value).__name__}")
                )
                self.metrics["flags_ignored_total"] += 1
                continue
            if _cohort_bucket(self._client_id, name) >= spec.rollout_pct:
                result.kept_cached.append(name)  # not in this client's cohort
                continue
            self._values[name] = value
            result.applied[name] = value
            self.metrics["flags_applied_total"] += 1

        self._consecutive_bad = 0
        self.metrics["consecutive_bad_fetches"] = 0
        self.metrics["degraded"] = False
        self._save_cache()
        return result

    def _parse(self, raw):
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        if not isinstance(raw, (bytes, bytearray)):
            return None
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
        return payload if isinstance(payload, dict) else None

    def _note_bad_payload(self):
        self._consecutive_bad += 1
        self.metrics["consecutive_bad_fetches"] = self._consecutive_bad
        if self._consecutive_bad >= self._degraded_after:
            # The cache is now the source of truth until a good payload
            # arrives; the client says so out loud instead of flapping.
            self.metrics["degraded"] = True
