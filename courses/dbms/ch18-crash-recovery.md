---
layout: page
title: "DBMS Ch.18: Recovery"
permalink: /courses/dbms/ch18-crash-recovery/
---

# Chapter 18: Crash Recovery (ARIES)

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 18

The **ARIES** algorithm is the gold standard for database recovery. It assumes **WAL** (Write Ahead Logging).

## 18.1 Log Structure
The Log is a sequence of records on stable storage.
Each record has a **LSN (Log Sequence Number)**.
-   `prev_LSN`: Link to previous record for same transaction.
-   `transID`, `type` (Update, Commit, Abort).
-   `pageID`, `old_value`, `new_value`.

**Key Structures**:
1.  **Transaction Table**: Active Txs. Contains `last_LSN`.
2.  **Dirty Page Table (DPT)**: Pages in RAM modified but not written to disk. Contains `rec_LSN` (LSN of first change).

---

## 18.2 Checkpointing
Periodically, the DBMS writes a checkpoint to truncate the log.
-   **Fuzzy Checkpoint**: Save TransTable and DPT to log. Do *not* flush dirt pages (too slow).

---

## 18.3 The 3 Phases of Recovery

### 1. Analysis Phase
Scan Log forward from last Checkpoint.
-   Reconstruct Transaction Table and DPT.
-   Identify "Winners" (Committed) and "Losers" (Active at crash).

### 2. Redo Phase (Repeating History)
Scan Log forward from smallest `rec_LSN` in DPT.
-   Re-apply **ALL** updates (even for Losers!).
-   This restores the DB to the *exact state* at the moment of crash.
-   **CLRs (Compensation Log Records)**: Redo them too.

### 3. Undo Phase
Scan Log backward.
-   For each Loser Tx, undo its actions using `old_value`.
-   Write a CLR for each undo (to ensure we don't undo the undo if we crash again).

Result: The DB is consistent. Atomicity and Durability preserved.
