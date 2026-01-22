---
layout: page
title: "DBMS Ch.17: Concurrency Control"
permalink: /courses/dbms/ch17-concurrency-control/
---

# Chapter 17: Concurrency Control

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 17

How do we guarantee Isolation? **Locking**.

## 17.1 Two-Phase Locking (2PL)
Protocol:
1.  **Phase 1 (Growing)**: Acquire locks. Cannot release any.
2.  **Phase 2 (Shrinking)**: Release locks. Cannot acquire any.
- **Strict 2PL**: Hold all exclusive locks until commit. (Prevents cascading aborts).

## 17.2 Lock Types
- **Shared (S)**: Read. Others can read too.
- **Exclusive (X)**: Write. No one else can touch.

## 17.3 Deadlocks
T1 holds A, wants B. T2 holds B, wants A.
- **Wait-for Graph**: Cycle detection.
- **Resolution**: Abort victim.

## 17.4 Other Approaches
- **Timestamp Ordering**: Assign timestamp to Tx. Abort if order violated.
- **Optimistic Concurrency Control (OCC)**: Read, Validate, Write.
