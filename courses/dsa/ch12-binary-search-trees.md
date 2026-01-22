---
layout: page
title: "DSA Ch.12: BST"
permalink: /courses/dsa/ch12-binary-search-trees/
---

# Chapter 12: Binary Search Trees (BST)

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 12

## 12.1 BST Property
For any node $x$:
-   If $y$ is in Left Subtree of $x$, then $y.key \le x.key$.
-   If $y$ is in Right Subtree of $x$, then $y.key \ge x.key$.

This allows **Inorder Traversal** to print sorted keys in $O(n)$.

## 12.2 Operations
All basic operations take $O(h)$ time, where $h$ is height.
-   **Search**: Trace down.
-   **Minimum**: Go left until null.
-   **Successor**:
    1.  If right subtree exists: Minimum of Right.
    2.  Else: Go up until we turn Right.
-   **Insert**: Trace down to leaf, attach.
-   **Delete**:
    1.  No children: Just remove.
    2.  One child: Splice out.
    3.  Two children: Find Successor (in right subtree), replace content, delete successor.

## 12.3 Randomly Built BSTs
If keys inserted in random order, expected height is $O(\lg n)$.
Worst case (sorted input): $O(n)$ chain.
