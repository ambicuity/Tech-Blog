---
layout: page
title: "DBMS Ch.10: B+ Trees"
permalink: /courses/dbms/ch10-tree-indexing/
---

# Chapter 10: Tree-Structured Indexing

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 10

The **B+ Tree** is the most standard index structure in databases. It is a dynamic, balanced tree that adjusts to changes.

## 10.1 ISAM (Indexed Sequential Access Method)
Static structure.
- Allocate file sequentially. Create index.
- Problem: If many inserts, we must create **overflow chains**. Performance degrades.

## 10.2 B+ Tree
- **Balanced**: All leaf nodes are at the same depth.
- **Node Structure**: Contains $m$ entries and $m+1$ pointers.
- **Occupancy**: Each node is at least 50% full (except root).
- **Properties**:
    - Search: $O(\log_F N)$ where $F$ is fanout (often ~100).
    - Insert: Find leaf. If full, **split** node and push middle key up.
    - Delete: Find leaf. If < 50% full, **merge** with sibling or borrow keys.

## 10.3 Why B+ Trees?
- Wide fanout means very low height (3 or 4).
- Leaves are linked in a chain $\to$ Fast sequential scan (Range Queries).
