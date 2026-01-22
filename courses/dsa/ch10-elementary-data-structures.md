---
layout: page
title: "DSA Ch.10: Elementary DS"
permalink: /courses/dsa/ch10-elementary-data-structures/
---

# Chapter 10: Elementary Data Structures

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 10

## 10.1 Stacks and Queues
-   **Stack**: LIFO (Last-In First-Out). `Push`, `Pop`. Implemented with array and `top` pointer. $O(1)$.
-   **Queue**: FIFO. `Enqueue`, `Dequeue`. Implemented with array and `head`, `tail` pointers (wrapping around). $O(1)$.

## 10.2 Linked Lists
Objects arranged in linear order.
-   **Doubly Linked**: `prev`, `next`, `key`.
-   **Sentinel**: A dummy object `nil` to simplify boundary conditions (no need to check `if x.next == null`).

## 10.3 Geometric Representation
Trees and Graphs are usually implemented using pointer-based nodes.
-   **Binary Tree**: `left`, `right`, `p` (parent).
-   **Unbounded Branching**: `left-child`, `right-sibling` representation.
