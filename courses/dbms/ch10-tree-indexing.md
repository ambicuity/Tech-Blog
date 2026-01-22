---
layout: page
title: "DBMS Ch.10: B+ Trees"
permalink: /courses/dbms/ch10-tree-indexing/
---

# Chapter 10: Tree-Structured Indexing (B+ Trees)

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 10

The **B+ Tree** is the most widely used index structure in relational databases. It is designed specifically for storage on **Disk** (Secondary Storage), minimizing the number of I/O operations required to find a record.

## 10.1 Why not Binary Search Trees (AVL/Red-Black)?
Binary trees have a **Fanout** of 2.
- To store $N=1,000,000$ keys, the height is $\log_2(10^6) \approx 20$.
- In a naive disk implementation, this means 20 Disk Seeks.
- 20 seeks $\times$ 10ms = 200ms per lookup. Too slow!

**B+ Tree Solution**: Increase Fanout ($F$).
- If we make the node size equal to a Disk Page (e.g., 4KB), we can fit hundreds of keys in one node.
- If $F=100$, then height is $\log_{100}(10^6) = 3$.
- 3 Disk Seeks = 30ms. Much fast.

---

## 10.2 Structure of a B+ Tree
A B+ Tree of order $d$:
1.  **Balanced**: All leaf nodes are at the same depth.
2.  **Internal Nodes**: Guide the search. Do *not* contain data pointers, only keys.
    - Stores between $d$ and $2d$ keys.
3.  **Leaf Nodes**: Contain the actual data entries (key, record-pointer).
    - Stores between $d$ and $2d$ data entries.
    - **Linked**: All leaves are linked in a sorted doubly-linked list (efficient specifically for **Range Queries**).

```mermaid
graph TD
    Root((Root: [13]))
    Root --> L1[Node: 5, 10]
    Root --> L2[Node: 20, 30]
    
    L1 --> Leaf1[Leaf: 2, 3, 5]
    L1 --> Leaf2[Leaf: 6, 8, 10]
    L1 --> Leaf3[Leaf: 11, 12]
    
    L2 --> Leaf4[Leaf: 14, 16, 20]
    L2 --> Leaf5[Leaf: 22, 25, 30]
```

---

## 10.3 Operations

### Search
1.  Start at Root.
2.  Compare search key $k$ with keys in node. Find sub-tree pointer that covers the range.
3.  Repeat until Leaf.
4.  Scan leaf for $k$.

### Insertion (The Split Algorithm)
We want to insert key $k$.
1.  **Find** the correct leaf node $L$.
2.  **Insert** entry into $L$.
3.  **Check for Overflow**:
    - If $L$ has $\le 2d$ entries: Done.
    - If $L$ has $> 2d$ entries: **Split**.
        - Create new leaf $L'$.
        - Move the second half of entries to $L'$.
        - **Copy up** the middle key to the parent.
4.  **Propagate**: If parent overflows, split parent and **Push up** the middle key.
    - *Note*: Difference between "Copy up" (Leaf split) and "Push up" (Internal split).

#### Example: Inserting 8 into a full node [2, 3, 5, 7] (Order d=2)
1.  Node becomes [2, 3, 5, 7, 8] (Overflow!).
2.  Split:
    - $L = [2, 3]$
    - $L' = [5, 7, 8]$
3.  Copy middle key **5** to parent.

### Deletion
1.  Find leaf. Remove entry.
2.  **Check for Underflow**:
    - If node has $< d$ entries.
    - Try to **Redistribute** (borrow) from sibling.
    - If sibling is barely full, **Merge** with sibling.
    - If merging, delete separating key from parent (recursively).

---

## 10.4 Bulk Loading
If we have a huge file, inserting records one-by-one is slow ($O(N \log N)$ random I/Os).
**Bulk Loading**:
1.  Sort all data entries.
2.  Fill leaf pages sequentially.
3.  Build index layer by layer from bottom up.
- Result: Perfectly packed tree, minimal fragments.

## 10.5 Cost Analysis
Let $F$ be fanout (~100), $N$ be number of pages.
- **Search**: $O(\log_F N)$ I/Os.
- **Insert/Delete**: $O(\log_F N)$ I/Os.
- **Range Scan**: Find start leaf, then follow `next` pointers. Cost: $T_{Search} + T_{SequentialScan}$.
