---
layout: page
title: "DBMS Ch.18: Recovery"
permalink: /courses/dbms/ch18-crash-recovery/
---

# Chapter 18: Crash Recovery (AHEAD/ARIES)

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 18

How to ensure Atomicity and Durability even if power plug is pulled?
**ARIES Algorithm** (Algorithms for Recovery and Isolation Exploiting Semantics).

## 18.1 Steal / No-Force
- **Steal**: Can buffer manager write an uncommitted page to disk? YES (to free up RAM).
- **No-Force**: Must buffer manager write all pages to disk at commit? NO (for performance).
This is the hardest combination (Undo/Redo required).

## 18.2 The Log (WAL)
Write-Ahead Logging protocol:
1.  Must write log record for update *before* page is written to disk.
2.  Must write commit record to log *before* acknowledge to user.
Log Sequence Number (**LSN**).

## 18.3 ARIES Phases
On restart after crash:
1.  **Analysis**: Scan log forward. Determine winners (committed) and losers (active at crash). Build Dirty Page Table.
2.  **Redo**: Scan forward again. Replay ALL actions (even losers). Restore DB to state at crash.
3.  **Undo**: Scan backward. Undo actions of Losers.
