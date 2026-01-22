---
layout: page
title: "DBMS Ch.15: Query Optimizer"
permalink: /courses/dbms/ch15-query-optimizer/
---

# Chapter 15: A Typical Relational Query Optimizer

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 15

Based on the **System R** optimizer (IBM).

## 15.1 Architecture
1.  **Parser**: SQL $\to$ Operator Tree.
2.  **Plan Enumerator**: Generates equivalent plans.
3.  **Cost Estimator**: Assigns cost to each plan.
4.  **Pick Best**: Chooses cheapest plan.

## 15.2 Statistics (System Catalog)
The DBMS stores stats in the catalog to estimate costs:
- `N`: Number of tuples.
- `B`: Number of blocks.
- `V(A, R)`: Number of distinct values for attribute A in R.
- Histogram of values (for skew).

## 15.3 Plan Enumeration
- **Left-Deep Trees**: Only allowed structure in System R (inner operand of join is base table).
    - Optimizes for Pipelining (no need to materialize intermediate joins).
- **Dynamic Programming**:
    - Best plan for $\{A, B, C\}$ = Union of Best plan for $\{A, B\} \bowtie C$, $\{A, C\} \bowtie B$, etc.

## 15.4 Selectivity
Estimate fraction of rows matching condition.
- `age = 20`: $1 / V(age, R)$.
- `age > 20`: $(Max - 20) / (Max - Min)$.
