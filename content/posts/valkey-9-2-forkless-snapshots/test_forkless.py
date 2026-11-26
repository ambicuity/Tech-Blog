"""Tests for the Valkey 9.2 forkless-snapshot article.

Run from the article folder against a real Valkey 9.2.1 build::

    VALKEY_SERVER=/path/to/valkey-server python3 -m pytest test_forkless.py -v

The server tests are skipped with a clear message when no binary is
available (VALKEY_SERVER, else ``valkey-server`` on PATH). The pure-logic
tests (RESP parsing, INFO parsing) always run. All tests that need a
server start their own instance on port 6390 with a throwaway directory
and shut it down with SHUTDOWN NOSAVE.

Versions: Valkey 9.2.1, Python 3.12.3, pytest 9.2.0.
"""

import os
import shutil
import socket
import tempfile

import pytest

from forkless_probe import (
    RespClient,
    Server,
    lat_stats,
    load_dataset,
    parse_info,
    run_bgsave,
    wait_bgsave_done,
)

SERVER = os.environ.get("VALKEY_SERVER") or shutil.which("valkey-server")
needs_server = pytest.mark.skipif(
    not SERVER, reason="no valkey-server binary (set VALKEY_SERVER)")
PORT = 6390


# ---------------------------------------------------------------------------
# Pure-logic tests: no server needed
# ---------------------------------------------------------------------------


def _client_from_socketpair(canned_reply):
    """A RespClient reading a canned RESP reply from a socketpair."""
    client_sock, server_sock = socket.socketpair()
    server_sock.sendall(canned_reply)
    server_sock.close()
    client = RespClient.__new__(RespClient)
    client._sock = client_sock
    client._buf = bytearray()
    return client


def test_resp_parses_all_reply_types():
    client = _client_from_socketpair(
        b"+OK\r\n:42\r\n$5\r\nhello\r\n$-1\r\n*3\r\n$1\r\na\r\n$1\r\nb\r\n$-1\r\n")
    assert client._read_reply() == "OK"
    assert client._read_reply() == 42
    assert client._read_reply() == b"hello"
    assert client._read_reply() is None
    assert client._read_reply() == [b"a", b"b", None]
    client.close()


def test_resp_error_raises():
    from forkless_probe import RespError
    client = _client_from_socketpair(b"-ERR something broke\r\n")
    with pytest.raises(RespError, match="something broke"):
        client._read_reply()
    client.close()


def test_parse_info_skips_comments_and_blank_lines():
    info = parse_info(
        "# Persistence\r\n"
        "rdb_bgsave_in_progress:0\r\n"
        "rdb_last_bgsave_type:forkless\r\n"
        "\r\n"
        "# Memory\r\n"
        "used_memory:12345\r\n")
    assert info == {
        "rdb_bgsave_in_progress": "0",
        "rdb_last_bgsave_type": "forkless",
        "used_memory": "12345",
    }


def test_lat_stats_empty():
    assert lat_stats([]) == {"n": 0}


# ---------------------------------------------------------------------------
# Server tests
# ---------------------------------------------------------------------------


@needs_server
def test_forkless_bgsave_reports_forkless():
    with tempfile.TemporaryDirectory(prefix="valkey-test-") as workdir:
        with Server(SERVER, PORT, workdir, True) as server:
            client = server.client()
            try:
                load_dataset(client, 1000, 64, seed=1)
                client.execute("BGSAVE")
                final = wait_bgsave_done(client)
                assert final["rdb_last_bgsave_type"] == "forkless"
                assert final["rdb_last_bgsave_status"] == "ok"
            finally:
                client.close()


@needs_server
def test_fork_bgsave_reports_fork():
    with tempfile.TemporaryDirectory(prefix="valkey-test-") as workdir:
        with Server(SERVER, PORT, workdir, False) as server:
            client = server.client()
            try:
                load_dataset(client, 1000, 64, seed=1)
                client.execute("BGSAVE")
                final = wait_bgsave_done(client)
                assert final["rdb_last_bgsave_type"] == "fork"
                assert final["rdb_last_bgsave_status"] == "ok"
            finally:
                client.close()


@needs_server
def test_policy_refused_without_infrastructure():
    """CONFIG SET forkless-policy prefer-forkless is refused when the
    server did not start with forkless-infrastructure-enabled yes."""
    from forkless_probe import RespError
    with tempfile.TemporaryDirectory(prefix="valkey-test-") as workdir:
        with Server(SERVER, PORT, workdir, False) as server:
            client = server.client()
            try:
                with pytest.raises(RespError):
                    client.execute("CONFIG", "SET", "forkless-policy",
                                   "prefer-forkless")
                policy = client.execute("CONFIG", "GET", "forkless-policy")
                assert policy[1] == b"require-fork"
            finally:
                client.close()


@needs_server
def test_snapshot_roundtrip_forkless():
    """A forkless BGSAVE writes an RDB the server can restart from."""
    with tempfile.TemporaryDirectory(prefix="valkey-test-") as workdir:
        with Server(SERVER, PORT, workdir, True) as server:
            client = server.client()
            try:
                load_dataset(client, 500, 64, seed=1)
                client.execute("BGSAVE")
                wait_bgsave_done(client)
                assert client.execute("DBSIZE") == 500
                assert client.execute("GET", "k:42") == b"v" * 64
            finally:
                client.close()
        with Server(SERVER, PORT, workdir, True) as server:
            client = server.client()
            try:
                assert client.execute("DBSIZE") == 500
                assert client.execute("GET", "k:42") == b"v" * 64
            finally:
                client.close()


@needs_server
def test_forkless_peak_memory_below_fork():
    """Same dataset, same write load: the forkless save's peak extra
    memory is less than half the fork save's. (Measured at 100k x 1 KiB
    keys: 1.1 MB vs 52.7 MB mean.)"""
    peaks = {}
    for forkless in (False, True):
        with tempfile.TemporaryDirectory(prefix="valkey-test-") as workdir:
            with Server(SERVER, PORT, workdir, forkless) as server:
                client = server.client()
                try:
                    load_dataset(client, 20000, 1024, seed=1)
                    result = run_bgsave(
                        client, server,
                        {"keys": 20000, "value_size": 1024, "seed": 7})
                    peaks[forkless] = result["peak_extra_mb"]
                    assert result["rdb_last_bgsave_status"] == "ok"
                finally:
                    client.close()
    assert peaks[True] < 0.5 * peaks[False], peaks


@needs_server
def test_large_write_latency_bounded_during_forkless_save():
    """Writes to large (256 KiB) keys during a forkless save stay bounded:
    p99 under 10 ms. (Measured p99 2.2-2.6 ms at 50k keys.)"""
    with tempfile.TemporaryDirectory(prefix="valkey-test-") as workdir:
        with Server(SERVER, PORT, workdir, True) as server:
            client = server.client()
            try:
                load_dataset(client, 20000, 1024, prefix="k", seed=1)
                load_dataset(client, 20, 262144, prefix="big", seed=2)
                result = run_bgsave(
                    client, server,
                    {"keys": 20000, "value_size": 100, "seed": 7,
                     "large_every": 20, "large_size": 262144})
                large = result["large_latency"]
                assert large["n"] >= 10
                assert large["p99_ms"] < 10.0, large
            finally:
                client.close()


@needs_server
def test_infrastructure_overhead_per_key():
    """The forkless infrastructure costs a small fixed amount per key.
    The docs say 4 bytes of metadata per key; used_memory measures 8
    bytes per key on jemalloc (one size class up). Assert the measured
    value stays in that band."""
    measured = {}
    for mode in ("off", "on"):
        with tempfile.TemporaryDirectory(prefix="valkey-test-") as workdir:
            with Server(SERVER, PORT, workdir, mode == "on") as server:
                client = server.client()
                try:
                    load_dataset(client, 100000, 16, seed=1)
                    info = parse_info(client.execute("INFO", "memory").decode())
                    measured[mode] = int(info["used_memory"])
                finally:
                    client.close()
    per_key = (measured["on"] - measured["off"]) / 100000
    assert 4.0 <= per_key <= 16.0, per_key
