---
layout: page
title: "DBMS Ch.12: Query Evaluation"
permalink: /courses/dbms/ch12-query-evaluation/
---

# Chapter 12: Overview of Query Evaluation

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 12

How does the DBMS execute a query like `SELECT * FROM S WHERE age=20`?

## 12.1 The Query Plan
A tree of relational operators annotated with choice of algorithms.
- **Relational Algebra Tree**: $\pi_{name}(\sigma_{age=20}(Students))$
- **Physical Plan**: Use IndexScan on `age` index -> Project Name.

## 12.2 Operator Implementation
1.  **Selection**: File Scan vs Index Scan.
2.  **Join**:
    - **Nested Loops Join**: For each row in A, scan B. $O(N^2)$.
    - **Sort-Merge Join**: Sort A and B on join column. Merge.
    - **Hash Join**: Partition A and B by hash of join column. Join partitions.
    - **Index Nested Loops**: For each row in A, look up B using index.

## 12.3 Pipelining
Operators do not materialize all results to disk. They `next()` tuples to parent.
- Example: `Filter` asks `Scan` for next tuple. If it matches, returns it to `Project`.
- Low memory footprint.
