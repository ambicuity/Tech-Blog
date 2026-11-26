#!/usr/bin/env python3
"""Measure Valkey 9.2 forkless vs fork BGSAVE behaviour on a real server.

Stdlib only. Starts a real ``valkey-server`` subprocess (built from the
Valkey 9.2.1 source), loads a dataset, runs BGSAVE under a write load, and
reports what the machine actually paid:

* ``rss``      -- peak extra memory (sum of Pss over the server process
                  group) during BGSAVE, fork vs forkless, plus save time
                  and the INFO persistence fields.
* ``latency``  -- write latency during BGSAVE, split by small-value SETs
                  (100 byte values, cloned from the fast-copy pool) and
                  large-value SETs (256 KiB values, which cannot be cloned
                  and must wait for the background thread).
* ``overhead`` -- used_memory with forkless infrastructure off vs on for
                  the same key count, i.e. the measured bytes per key.
* ``smoke``    -- one forkless BGSAVE and a snapshot round-trip check.

Usage (run from the article folder; VALKEY_SERVER or --server points at
the built binary)::

    python3 forkless_probe.py rss --server /path/to/valkey-server \
        --mode fork --keys 100000 --value-size 1024 --runs 3
    python3 forkless_probe.py latency --server /path/to/valkey-server \
        --mode forkless
    python3 forkless_probe.py overhead --server /path/to/valkey-server \
        --keys 200000

Everything printed is JSON on stdout so the numbers in the article can be
regenerated. The server is started with a real config file (the forkless
infrastructure flag is immutable and must be set at startup) and shut
down with SHUTDOWN NOSAVE at the end of each run.
"""

import argparse
import json
import math
import os
import random
import socket
import statistics
import subprocess
import sys
import tempfile
import threading
import time

# ---------------------------------------------------------------------------
# Minimal RESP client (stdlib only)
# ---------------------------------------------------------------------------


class RespError(Exception):
    pass


class RespClient:
    """A small synchronous RESP2 client over one TCP connection."""

    def __init__(self, port, timeout=30.0):
        self._sock = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        self._buf = bytearray()

    def close(self):
        try:
            self._sock.close()
        except OSError:
            pass

    def _readline(self):
        while True:
            idx = self._buf.find(b"\r\n")
            if idx >= 0:
                line = bytes(self._buf[:idx])
                del self._buf[: idx + 2]
                return line
            chunk = self._sock.recv(65536)
            if not chunk:
                raise ConnectionError("server closed the connection")
            self._buf += chunk

    def _read_exact(self, n):
        while len(self._buf) < n:
            chunk = self._sock.recv(65536)
            if not chunk:
                raise ConnectionError("server closed the connection")
            self._buf += chunk
        out = bytes(self._buf[:n])
        del self._buf[:n]
        return out

    def _read_reply(self):
        line = self._readline()
        kind, payload = line[:1], line[1:]
        if kind == b"+":
            return payload.decode()
        if kind == b"-":
            raise RespError(payload.decode())
        if kind == b":":
            return int(payload)
        if kind == b"$":
            n = int(payload)
            if n == -1:
                return None
            data = self._read_exact(n + 2)
            return data[:-2]
        if kind == b"*":
            n = int(payload)
            if n == -1:
                return None
            return [self._read_reply() for _ in range(n)]
        raise RespError(f"unexpected reply prefix {kind!r}")

    def execute(self, *args):
        parts = [f"*{len(args)}\r\n".encode()]
        for arg in args:
            if isinstance(arg, str):
                arg = arg.encode()
            parts.append(f"${len(arg)}\r\n".encode())
            parts.append(arg)
            parts.append(b"\r\n")
        self._sock.sendall(b"".join(parts))
        return self._read_reply()

    def pipeline(self, commands):
        """Send many commands at once, read that many replies. Returns the list."""
        out = bytearray()
        for args in commands:
            out += f"*{len(args)}\r\n".encode()
            for arg in args:
                if isinstance(arg, str):
                    arg = arg.encode()
                out += f"${len(arg)}\r\n".encode()
                out += arg
                out += b"\r\n"
        self._sock.sendall(bytes(out))
        return [self._read_reply() for _ in commands]


def parse_info(text):
    """Parse INFO output into a flat dict of str->str."""
    info = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            info[key] = value
    return info


# ---------------------------------------------------------------------------
# Server lifecycle
# ---------------------------------------------------------------------------


class Server:
    """One valkey-server subprocess, started from a written config file."""

    def __init__(self, binary, port, workdir, forkless, extra=None):
        self.binary = binary
        self.port = port
        self.workdir = workdir
        self.forkless = forkless
        self.proc = None
        conf = os.path.join(workdir, "valkey.conf")
        lines = [
            f"port {port}",
            "bind 127.0.0.1",
            "protected-mode no",
            "daemonize no",
            'dir "%s"' % workdir,
            "dbfilename dump.rdb",
            'save ""',
            "appendonly no",
            "maxmemory 0",
            "logfile ''",
        ]
        if forkless:
            lines.append("forkless-infrastructure-enabled yes")
            lines.append("forkless-policy prefer-forkless")
        else:
            lines.append("forkless-infrastructure-enabled no")
            lines.append("forkless-policy require-fork")
        if extra:
            lines.extend(extra)
        with open(conf, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        self.conf = conf

    def __enter__(self):
        self.proc = subprocess.Popen(
            [self.binary, self.conf],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.time() + 20
        try:
            while True:
                try:
                    client = RespClient(self.port, timeout=5.0)
                except (ConnectionError, OSError):
                    if time.time() > deadline:
                        raise RuntimeError("server did not answer PING in 20s")
                    time.sleep(0.05)
                    continue
                try:
                    if client.execute("PING") == "PONG":
                        break
                except (ConnectionError, OSError, RespError):
                    client.close()
                    if time.time() > deadline:
                        raise RuntimeError("server did not answer PING in 20s")
                    time.sleep(0.05)
            client.close()
        except Exception:
            # Never leak the subprocess when startup fails (e.g. the port
            # is already taken): a stale server on this port would poison
            # the next run by answering PING with the wrong config.
            self.proc.kill()
            self.proc.wait(timeout=10)
            raise
        return self

    def __exit__(self, *exc):
        try:
            client = RespClient(self.port, timeout=5.0)
            try:
                client.execute("SHUTDOWN", "NOSAVE")
            except (ConnectionError, OSError):
                pass  # SHUTDOWN closes the connection; that is expected
            client.close()
        except (ConnectionError, OSError):
            pass
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=10)
        return False

    def client(self):
        return RespClient(self.port)


# ---------------------------------------------------------------------------
# Memory sampling: sum of Pss over the server process group
# ---------------------------------------------------------------------------


def read_pss(pid):
    """Proportional set size (bytes) of one process, or None if gone."""
    try:
        with open(f"/proc/{pid}/smaps_rollup", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("Pss:"):
                    return int(line.split()[1]) * 1024
    except (FileNotFoundError, ProcessLookupError, ValueError):
        return None
    return None


def child_pids(pid):
    """Direct children of pid, via /proc/*/status PPid."""
    children = []
    try:
        entries = os.listdir("/proc")
    except OSError:
        return children
    for entry in entries:
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/status", encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("PPid:"):
                        if int(line.split()[1]) == pid:
                            children.append(int(entry))
                        break
        except (FileNotFoundError, ProcessLookupError, ValueError):
            continue
    return children


def group_pss(pid):
    """Sum of Pss for pid and its direct children (the fork child)."""
    total = 0
    seen = False
    for p in [pid] + child_pids(pid):
        pss = read_pss(p)
        if pss is not None:
            total += pss
            seen = True
    return total if seen else None


# ---------------------------------------------------------------------------
# Dataset loading and writers
# ---------------------------------------------------------------------------


def load_dataset(client, n_keys, value_size, prefix="k", seed=1):
    """Load n_keys string keys of value_size bytes, pipelined in batches."""
    rng = random.Random(seed)
    value = ("v" * value_size).encode()
    batch = []
    loaded = 0
    for i in range(n_keys):
        batch.append(("SET", f"{prefix}:{i}", value))
        if len(batch) == 1000:
            client.pipeline(batch)
            loaded += len(batch)
            batch = []
    if batch:
        client.pipeline(batch)
        loaded += len(batch)
    return loaded


class Writer(threading.Thread):
    """Hammer SETs on random keys until stopped; records per-op latency."""

    def __init__(self, port, keys, value_size, prefix="k", seed=7, large_every=0,
                 large_size=0, large_prefix="big"):
        super().__init__(daemon=True)
        self.port = port
        self.keys = keys
        self.value_size = value_size
        self.prefix = prefix
        self.seed = seed
        self.large_every = large_every
        self.large_size = large_size
        self.large_prefix = large_prefix
        self.stop_flag = threading.Event()
        self.small_lat = []
        self.large_lat = []
        self.ops = 0
        self.errors = []

    def run(self):
        rng = random.Random(self.seed)
        small_value = ("s" * self.value_size).encode()
        large_value = ("L" * self.large_size).encode() if self.large_size else b""
        try:
            client = RespClient(self.port, timeout=30.0)
        except OSError as exc:
            self.errors.append(str(exc))
            return
        n = 0
        try:
            while not self.stop_flag.is_set():
                n += 1
                if self.large_every and n % self.large_every == 0:
                    key = f"{self.large_prefix}:{rng.randrange(100)}"
                    t0 = time.perf_counter()
                    client.execute("SET", key, large_value)
                    self.large_lat.append(time.perf_counter() - t0)
                else:
                    key = f"{self.prefix}:{rng.randrange(self.keys)}"
                    t0 = time.perf_counter()
                    client.execute("SET", key, small_value)
                    self.small_lat.append(time.perf_counter() - t0)
                self.ops += 1
        except (ConnectionError, OSError, RespError) as exc:
            self.errors.append(str(exc))
        finally:
            client.close()

    def stop(self):
        self.stop_flag.set()


def percentile(values, pct):
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, math.ceil(pct / 100.0 * len(ordered)) - 1))
    return ordered[idx]


def lat_stats(latencies):
    if not latencies:
        return {"n": 0}
    seconds = latencies
    return {
        "n": len(seconds),
        "mean_ms": round(statistics.mean(seconds) * 1000, 3),
        "p50_ms": round(percentile(seconds, 50) * 1000, 3),
        "p99_ms": round(percentile(seconds, 99) * 1000, 3),
        "max_ms": round(max(seconds) * 1000, 3),
    }


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------


def wait_bgsave_done(client, timeout=300):
    """Poll INFO until no BGSAVE is in progress; return the final INFO dict."""
    deadline = time.time() + timeout
    while True:
        info = parse_info(client.execute("INFO", "persistence").decode())
        if info.get("rdb_bgsave_in_progress") == "0":
            return info
        if time.time() > deadline:
            raise RuntimeError("BGSAVE did not finish in %ss" % timeout)
        time.sleep(0.02)


def run_bgsave(client, server, writer_kwargs, sample_interval=0.025):
    """One BGSAVE under write load. Returns measurements."""
    baseline = group_pss(server.proc.pid)
    writer = Writer(server.port, **writer_kwargs)
    writer.start()
    info0 = parse_info(client.execute("INFO", "persistence").decode())
    t0 = time.time()
    client.execute("BGSAVE")
    peak = baseline
    samples = 0
    while True:
        info = parse_info(client.execute("INFO", "persistence").decode())
        current = group_pss(server.proc.pid)
        if current is not None:
            peak = max(peak, current)
            samples += 1
        if info.get("rdb_bgsave_in_progress") == "0":
            break
        time.sleep(sample_interval)
    duration = time.time() - t0
    writer.stop()
    writer.join(timeout=10)
    final = parse_info(client.execute("INFO", "persistence").decode())
    return {
        "baseline_group_pss_mb": round(baseline / 1e6, 1) if baseline else None,
        "peak_group_pss_mb": round(peak / 1e6, 1) if peak else None,
        "peak_extra_mb": round((peak - baseline) / 1e6, 1) if baseline and peak else None,
        "save_seconds": round(duration, 2),
        "samples": samples,
        "rdb_last_bgsave_type": final.get("rdb_last_bgsave_type"),
        "rdb_last_bgsave_status": final.get("rdb_last_bgsave_status"),
        "latest_fork_usec": final.get("latest_fork_usec"),
        "writer_ops": writer.ops,
        "writer_errors": writer.errors,
        "small_latency": lat_stats(writer.small_lat),
        "large_latency": lat_stats(writer.large_lat),
    }


def cmd_rss(args):
    results = []
    for run in range(args.runs):
        with tempfile.TemporaryDirectory(prefix="valkey-rss-") as workdir:
            with Server(args.server, args.port, workdir, args.mode == "forkless") as server:
                client = server.client()
                try:
                    loaded = load_dataset(client, args.keys, args.value_size, seed=1)
                    # Let the server settle: one full INFO round and a short pause.
                    time.sleep(0.5)
                    result = run_bgsave(
                        client, server,
                        {"keys": args.keys, "value_size": args.value_size, "seed": 7},
                    )
                    result["run"] = run + 1
                    result["mode"] = args.mode
                    result["keys_loaded"] = loaded
                    results.append(result)
                finally:
                    client.close()
    extras = [r["peak_extra_mb"] for r in results if r["peak_extra_mb"] is not None]
    summary = {
        "experiment": "rss",
        "mode": args.mode,
        "keys": args.keys,
        "value_size": args.value_size,
        "runs": results,
        "mean_peak_extra_mb": round(statistics.mean(extras), 1) if extras else None,
        "mean_save_seconds": round(
            statistics.mean([r["save_seconds"] for r in results]), 2),
    }
    print(json.dumps(summary, indent=2))
    return summary


def cmd_latency(args):
    results = []
    for run in range(args.runs):
        with tempfile.TemporaryDirectory(prefix="valkey-lat-") as workdir:
            with Server(args.server, args.port, workdir, args.mode == "forkless") as server:
                client = server.client()
                try:
                    load_dataset(client, args.keys, 1024, prefix="k", seed=1)
                    # 100 large keys the writer will overwrite during the save.
                    load_dataset(client, 100, args.large_size, prefix="big", seed=2)
                    time.sleep(0.5)
                    result = run_bgsave(
                        client, server,
                        {"keys": args.keys, "value_size": 100, "seed": 7,
                         "large_every": 20, "large_size": args.large_size},
                    )
                    result["run"] = run + 1
                    result["mode"] = args.mode
                    results.append(result)
                finally:
                    client.close()
    summary = {
        "experiment": "latency",
        "mode": args.mode,
        "keys": args.keys,
        "large_size": args.large_size,
        "runs": results,
        "mean_small_p99_ms": round(statistics.mean(
            [r["small_latency"]["p99_ms"] for r in results]), 3),
        "mean_large_p99_ms": round(statistics.mean(
            [r["large_latency"]["p99_ms"] for r in results]), 3),
        "mean_large_max_ms": round(statistics.mean(
            [r["large_latency"]["max_ms"] for r in results]), 3),
    }
    print(json.dumps(summary, indent=2))
    return summary


def cmd_overhead(args):
    """used_memory with the forkless infrastructure off vs on, same key count."""
    out = {}
    for mode in ("off", "on"):
        with tempfile.TemporaryDirectory(prefix="valkey-ovh-") as workdir:
            with Server(args.server, args.port, workdir, mode == "on") as server:
                client = server.client()
                try:
                    load_dataset(client, args.keys, args.value_size, seed=1)
                    time.sleep(0.3)
                    info = parse_info(client.execute("INFO", "memory").decode())
                    out[mode] = {
                        "used_memory": int(info["used_memory"]),
                        "used_memory_rss": int(info["used_memory_rss"]),
                        "mem_allocator": info.get("mem_allocator"),
                    }
                finally:
                    client.close()
    delta = out["on"]["used_memory"] - out["off"]["used_memory"]
    summary = {
        "experiment": "overhead",
        "keys": args.keys,
        "value_size": args.value_size,
        "off": out["off"],
        "on": out["on"],
        "used_memory_delta_bytes": delta,
        "bytes_per_key": round(delta / args.keys, 2),
    }
    print(json.dumps(summary, indent=2))
    return summary


def cmd_smoke(args):
    """One forkless BGSAVE, then restart from the RDB and verify the data."""
    with tempfile.TemporaryDirectory(prefix="valkey-smoke-") as workdir:
        with Server(args.server, args.port, workdir, True) as server:
            client = server.client()
            try:
                load_dataset(client, 1000, 64, seed=1)
                client.execute("BGSAVE")
                final = wait_bgsave_done(client)
                assert final.get("rdb_last_bgsave_type") == "forkless", final
                assert final.get("rdb_last_bgsave_status") == "ok", final
                before = client.execute("DBSIZE")
                assert client.execute("GET", "k:42") == b"v" * 64
            finally:
                client.close()
        # Restart from the snapshot the save wrote and check the data is there.
        with Server(args.server, args.port, workdir, True) as server:
            client = server.client()
            try:
                after = client.execute("DBSIZE")
                value = client.execute("GET", "k:42")
                assert after == before, (after, before)
                assert value == b"v" * 64, value
            finally:
                client.close()
    print(json.dumps({"experiment": "smoke", "ok": True, "keys": 1000}, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", required=True, help="path to valkey-server")
    parser.add_argument("--port", type=int, default=6390)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("rss")
    p.add_argument("--mode", choices=["fork", "forkless"], required=True)
    p.add_argument("--keys", type=int, default=100000)
    p.add_argument("--value-size", type=int, default=1024)
    p.add_argument("--runs", type=int, default=3)
    p.set_defaults(func=cmd_rss)
    p = sub.add_parser("latency")
    p.add_argument("--mode", choices=["fork", "forkless"], required=True)
    p.add_argument("--keys", type=int, default=50000)
    p.add_argument("--large-size", type=int, default=262144)
    p.add_argument("--runs", type=int, default=3)
    p.set_defaults(func=cmd_latency)
    p = sub.add_parser("overhead")
    p.add_argument("--keys", type=int, default=200000)
    p.add_argument("--value-size", type=int, default=16)
    p.set_defaults(func=cmd_overhead)
    p = sub.add_parser("smoke")
    p.set_defaults(func=cmd_smoke)
    args = parser.parse_args(argv)
    if not os.path.isfile(args.server) or not os.access(args.server, os.X_OK):
        print(f"valkey-server not found or not executable: {args.server}", file=sys.stderr)
        return 2
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
