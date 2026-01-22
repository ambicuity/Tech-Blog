---
layout: page
title: "DBMS Ch.17: Concurrency Control"
permalink: /courses/dbms/ch17-concurrency-control/
---

# Chapter 17: Concurrency Control

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 17

How do we implement the Isolation property?

## 17.1 Two-Phase Locking (2PL)
**Lock Manager** maintains a hash table of ResourceID $\to$ List of Locks.
-   **Shared (S)**: Read. Compatible with S.
-   **Exclusive (X)**: Write. Compatible with Nothing.

**Protocol**:
1.  **Growing Phase**: Acquire locks.
2.  **Shrinking Phase**: Release locks. (Cannot acquire anymore).
-   **Strict 2PL**: Hold X-locks until Commit. Prevents cascading aborts.

---

## 17.2 Deadlocks
T1 holds A, waits for B. T2 holds B, waits for A. Cycle!
1.  **Deadlock Prevention**: Assign priorities (Timestamps).
    -   *Wait-Die*: If Old waits for Young, wait. If Young waits for Old, die.
    -   *Wound-Wait*: If Old waits for Young, kill Young.
2.  **Deadlock Detection**: Maintain a **Wait-For Graph**. Periodically run cycle detection (BFS/DFS). If cycle found, pick a victim and abort.

---

## 17.3 Advanced Issues
### Phantom Problem
T1 scans `SELECT * FROM Sailors WHERE rating > 8`.
T2 inserts new sailor with rating 9.
T1 runs same query again, sees different result.
-   Cause: T1 locked *existing* rows, but T2 added a *new* row.
-   Solution: **Index Locking** (Key-Range Locking) or Predicate Locking.

### Isolation Levels
SQL allows trading correctness for performance.
1.  **Read Uncommitted**: Can read dirty data. (Fastest).
2.  **Read Committed**: Uncommitted data is hidden. (Standard).
3.  **Repeatable Read**: Re-reads are consistent (Locks held longer).
4.  **Serializable**: Full ACID.

---

## 17.4 Optimistic Concurrency Control (Kung & Robinson)
If conflicts are rare, locking is overhead.
1.  **Read Phase**: Execute privately.
2.  **Validation Phase**: Check for conflicts.
    -   If $WriteSet(T_i) \cap ReadSet(T_j) \neq \emptyset$, abort.
3.  **Write Phase**: Commit changes.
