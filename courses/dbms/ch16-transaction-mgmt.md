---
layout: page
title: "DBMS Ch.16: Transaction Mgmt"
permalink: /courses/dbms/ch16-transaction-mgmt/
---

# Chapter 16: Transaction Management

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 16

A transaction (Tx) is a sequence of reads/writes that transforms the DB from one consistent state to another.

## 16.1 The ACID Properties
1.  **Atomicity**: All or Nothing. If Tx crashes, changes must be undone.
    *   *Mechanism*: Write-Ahead Logging (WAL) + Undo.
2.  **Consistency**: Tx must preserve DB invariants (e.g., $A+B = 100$).
    *   *Mechanism*: User responsibility + Integrity Constraints.
3.  **Isolation**: Txs execute as if they are alone.
    *   *Mechanism*: Concurrency Control (Locks).
4.  **Durability**: Committed changes survive failures.
    *   *Mechanism*: WAL + Redo.

---

## 16.2 Scheduling and Serializability
How can we interleave T1 and T2 for performance without incorrectness?

### Serial Schedule
T1 runs to completion, then T2. Safe, but no parallelism.

### Serializable Schedule
Any schedule that produces the same effect as *some* serial schedule.

### Conflict Serializability
We check for **Conflicts**: Two actions on the same object, from different Txs, at least one is a Write.
-   Read-Write (RW), Write-Read (WR), Write-Write (WW).

**Precedence Graph**:
-   Nodes: Transactions.
-   Edge $T_i \to T_j$: If $T_i$ has an action that conflicts with and precedes an action in $T_j$.
-   **Theorem**: A schedule is Conflict Serializable $\iff$ Precedence Graph is Acyclic.

---

## 16.3 Recoverability
Not all schedules are recoverable.
**Cascading Abort**: If T1 writes X, T2 reads X, and T1 aborts $\to$ T2 must also abort.
**Strict Schedule**: A Tx can only read/write X if the Tx that last wrote X has committed.
*   Avoiding Cascading Aborts is crucial for performance.
*   Implementation: **Strict 2PL** (Hold Exclusive locks until commit).
