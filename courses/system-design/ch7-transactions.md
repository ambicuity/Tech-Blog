---
layout: page
title: "System Design Ch.7: Transactions"
permalink: /courses/system-design/ch7-transactions/
---

# Chapter 7: Transactions

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 7

A **transaction** is a way for an application to group several reads and writes together into a single logical unit.
Key concept: **ACID**.

## 7.1 The Meaning of ACID
- **Atomicity**: All or nothing. If it fails (abort), any partial writes are undone (rollback).
- **Consistency**: The application's invariants (e.g., Debits = Credits) must be true before and after. (Actually an application property, not database).
- **Isolation**: Concurrently executing transactions shouldn't interfere with each other.
- **Durability**: Once committed, data is safe (on disk/replicated).

## 7.2 Weak Isolation Levels
Serializable (perfect isolation) is expensive. Systems offer weaker guarantees.

### Read Committed
1.  **No Dirty Reads**: You only read data that has been committed.
2.  **No Dirty Writes**: You only overwrite data that has been committed.

### Snapshot Isolation (Repeatable Read)
- **Problem**: **Non-repeatable read**. (Alice sees account has 100. Bob pays 10. Alice reads again, sees 110).
- **Solution**: MVCC (Multi-Version Concurrency Control). Readers don't block writers; writers don't block readers. Reader sees a consistent snapshot from start of transaction.

## 7.3 Serializability
The gold standard.
1.  **Actual Serial Execution**: Run one transaction at a time on a single thread (Redis, VoltDB). Fast for RAM-based, short transactions.
2.  **2PL (Two-Phase Locking)**:
    - Shared lock for reading. Exclusive lock for writing.
    - Deadlocks are frequent.
3.  **SSI (Serializable Snapshot Isolation)**: Optimistic concurrency control. Detect conflicts at commit time and abort.
