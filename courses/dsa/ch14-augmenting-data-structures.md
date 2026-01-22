---
layout: page
title: "DSA Ch.14: Augmenting Data Structures"
permalink: /courses/dsa/ch14-augmenting-data-structures/
---

# Chapter 14: Augmenting Data Structures

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 14

Standard structures (RB-Trees, Hash Tables) aren't enough. We often need to store extra info to answer queries efficiently.

## 14.1 Dynamic Order Statistics
**Problem**: Find the $i$-th smallest element in a dynamic set (Insert/Delete allowed).
**Structure**: OS-Tree (Order Statistic Tree).
-   Basis: Red-Black Tree.
-   **Augmentation**: Add `size` field to every node. `x.size = x.left.size + x.right.size + 1`.

**Select(x, i)**:
-   Rank of current node $k = x.left.size + 1$.
-   If $i == k$, return x.
-   If $i < k$, recurse left.
-   If $i > k$, recurse right searching for $i - k$.
Time: $O(\log N)$.

## 14.2 Maintaining Augmentations
When we Rotate (during Insert/Delete balancing), we must update `size`.
Since `size` only depends on children, we can update it in $O(1)$ after rotation.
**Theorem**: If field $f$ depends only on node and children, we can maintain it in any RB-Tree operation without changing asymptotics.

## 14.3 Interval Trees
**Problem**: Store set of intervals $[low, high]$. Find any interval overlapping with query $[a, b]$.
**Augmented RB-Tree**:
-   Key: `low`.
-   Augmentation: `max` (maximum high value in subtree).
-   **Search**: Use `max` to decide whether to prune branches.
Time: $O(\log N)$.
