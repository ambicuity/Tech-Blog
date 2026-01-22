---
layout: page
title: "DBMS Ch.16: Transaction Mgmt"
permalink: /courses/dbms/ch16-transaction-mgmt/
---

# Chapter 16: Overview of Transaction Management

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 16

A transaction is a user program execution that is treated as a single logical unit.
Key concept: **ACID**.

## 16.1 Properties (ACID)
1.  **Atomicity**: All or nothing. (Crash Recovery).
2.  **Consistency**: DB states are valid (e.g., salary > 0).
3.  **Isolation**: Users feel like they are alone. (Concurrency Control).
4.  **Durability**: Written data is safe. (WAL - Write Ahead Logging).

## 16.2 Schedules
Interleaving actions from multiple transactions.
- **Serial Schedule**: T1 runs, then T2. Safe.
- **Serializable Schedule**: Equivalent to some serial schedule.

## 16.3 Anomalies
What if we don't lock?
- **Dirty Read**: Reading uncommitted data.
- **Unrepeatable Read**: Reading X, someone updates X, read X again (different).
- **Lost Update**: T1 and T2 increment X. Both read 10. Both write 11. (Should be 12).
