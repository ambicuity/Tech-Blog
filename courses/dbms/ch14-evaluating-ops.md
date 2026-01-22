---
layout: page
title: "DBMS Ch.14: Relational Ops"
permalink: /courses/dbms/ch14-evaluating-ops/
---

# Chapter 14: Evaluating Relational Operators

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 14

Implementation details of Select, Join, Project, Aggregate.

## 14.1 Selection ($\sigma$)
- **No Index**: Full Table Scan. Cost $N$.
- **Index**: Find first matching leaf, then scan matching data entries. Cost: Height + Matches.

## 14.2 Projection ($\pi$)
- Must remove duplicates (DISTINCT).
- Approach 1: Sort by projected attributes, then scan and remove adjacent duplicates.
- Approach 2: Hash Partitioning. Parition by hash of attributes. Duplicates will land in same bucket.

## 14.3 Join ($\bowtie$)
- **Block Nested Loops Join**: For each *block* of Outer, scan Inner.
    - Cost: $M + (M \times N)$, if Inner doesn't fit in RAM.
- **Sort-Merge Join**: Good if data is already sorted (e.g., on Clustered Index).
- **Hash Join**:
    1.  Partition both relations using $h1$.
    2.  Load partition of R into hash table using $h2$.
    3.  Probe with partition of S.
    - Linear Cost: $3(M+N)$. Often best for unsorted data.

## 14.4 Set Operations
- Union, Intersection, Difference can be implemented via Sorting or Hashing, similar to Join.
