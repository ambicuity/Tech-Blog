---
layout: page
title: "DBMS Ch.12: Query Evaluation"
permalink: /courses/dbms/ch12-query-evaluation/
---

# Chapter 12: Query Evaluation and Execution

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 12 & 14

How does the database engine physically execute SQL? It translates the query into a tree of **Relational Operators** (Iterators).

## 12.1 The Iterator Model
Every operator (Scan, Select, Join) implements a standard interface:
-   `open()`: Initialize.
-   `next()`: Return next tuple.
-   `close()`: Cleanup.

This allows **Pipelining**. Results are passed up tuple-at-a-time. No need to store huge intermediate results on disk.

---

## 12.2 External Merge Sort
Sorting is fundamental (for ORDER BY, GROUP BY, Sort-Merge Join).
Problem: Sort 10GB data with 1GB RAM.
**Algorithm**:
1.  **Pass 0**: Read 1GB chunks, sort in memory (Quicksort), write to disk as a **Run**. Result: 10 sorted runs.
2.  **Pass 1**: Use all available buffer pages to read from the 10 runs simultaneously. Merge them into a single sorted stream.

**Cost**: $2N \times (\#Passes)$.
Number of passes $\approx \log_{B}(N)$. Usually 2 passes is enough for Petabytes.

---

## 12.3 Join Algorithms
`R JOIN S ON R.id = S.id`

### 1. Simple Nested Loops Join
```python
for r in R:
    for s in S:
        if r.id == s.id: yield (r, s)
```
*   **Cost**: $M + (p_R \times M) \times N$. (Read R once. For every row in R, scan S). **Terrible**.

### 2. Block Nested Loops Join
Optimize I/O by reading a **Block** of R.
```python
for block_r in R:
    load_into_hash_table(block_r)
    for block_s in S:
        for s in block_s:
            check_hash_table(s)
```
*   **Cost**: $M + N \times (\frac{M}{B-2})$.

### 3. Sort-Merge Join
Sort R and S on join key. Scan them in parallel.
*   **Cost**: Cost(Sort R) + Cost(Sort S) + $(M+N)$.
*   Great if data is already sorted (Clustered Index).

### 4. Hash Join (The Workhorse)
1.  **Partitioning Phase**: Hash R and S using function $h_1$ into partitions $R_1 \dots R_k$ and $S_1 \dots S_k$. Only tuples in $R_i$ can match tuples in $S_i$.
2.  **Probing Phase**: Load $R_i$ into memory (build hash table $h_2$). Stream $S_i$ and probe.
*   **Cost**: $3(M+N)$. Linear time!
*   Requirement: Smaller partition must fit in memory.

---

## 12.4 Materialization vs Pipelining
*   **Pipelining**: `next()` call passes data. Low memory.
*   **Materialization**: Operator writes all results to a temporary table on disk. Next operator reads it. Required for sorts or when memory is tight.
