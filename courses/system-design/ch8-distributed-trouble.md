---
layout: page
title: "System Design Ch.8: Distributed Trouble"
permalink: /courses/system-design/ch8-distributed-trouble/
---

# Chapter 8: The Trouble with Distributed Systems

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 8

Distributed systems are different from single-node software because anything that *can* go wrong *will* go wrong. We must handle partial failures.

## 8.1 Faults and Partial Failures
In a single computer, if hardware fails, the machine crashes (total failure).
In a distributed system, some parts may be broken while others work perfectly. This **nondeterminism** makes distributed programming hard.

## 8.2 Unreliable Networks
The internet is an asynchronous packet-switched network.
- A request may be lost.
- A request may be waiting in a queue.
- The remote node may have failed.
- The response may be lost.
**Timeout**: The only way to detect a fault is to wait "long enough" and give up.

## 8.3 Unreliable Clocks
- **Time-of-day clocks**: `System.currentTimeMillis()`. Synced via NTP. Can jump back in time! **Never use for measuring duration**.
- **Monotonic clocks**: `System.nanoTime()`. Always goes forward. Good for measuring duration.
- **Clock Drift**: Quartz crystals drift (20s/day is possible).

**Impact**:
- Last Write Wins (LWW) depends on timestamps. If clocks are out of sync, we might lose data.
- **Google Spanner**: Uses "TrueTime" API (GPS + Atomic clocks) to bound clock uncertainty ($\epsilon$).

## 8.4 Knowledge, Truth, and Lies
- **The Truth is defined by the majority (Quorum)**. If a node is disconnected, it might think it's the leader, but the quorum disagrees.
- **Fencing Tokens**: Used to lock resources. Token number increases (1, 2, 3). If zombie client tries to write with token 1, storage rejects it because it has seen token 2.
- **Byzantine Faults**: When nodes lie (send malicious/incorrect data). Most systems assume non-Byzantine failures (nodes just crash).
