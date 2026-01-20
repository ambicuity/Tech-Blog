---
layout: page
title: "DSA Ch.6: Heapsort"
permalink: /courses/dsa/ch6-heapsort/
---

# Chapter 6: Heapsort

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 6

Heapsort is a sorting algorithm that introduces a new data structure: the **Heap**.
Like merge sort, its running time is $O(n \lg n)$. Like insertion sort, it sorts **in place** (no extra memory).

## 6.1 Heaps
The (binary) heap data structure is an array object that we can view as a nearly complete binary tree.
- **Parent(i)**: `floor(i/2)`
- **Left(i)**: `2i`
- **Right(i)**: `2i + 1`

### Max-Heap Property
For every node $i$ other than the root:
$$A[Parent(i)] \ge A[i]$$
The largest element is at the root. (Used for Heapsort).

### Min-Heap Property
$$A[Parent(i)] \le A[i]$$
The smallest element is at the root. (Used for Priority Queues).

## 6.2 Maintaining the Heap Property
`Max-Heapify(A, i)`: Assumes binary trees rooted at `Left(i)` and `Right(i)` are max-heaps, but $A[i]$ might be smaller than its children. It lets the value at $A[i]$ "float down".
- **Time Complexity**: $O(\lg n)$ (height of tree).

## 6.3 Building a Heap
`Build-Max-Heap(A)`: call `Max-Heapify` on all non-leaf nodes (from $n/2$ down to 1).
- **Time Complexity**: Linear time, $O(n)$. (Surprising, but rigorous proof exists).

## 6.4 The Heapsort Algorithm
1.  `Build-Max-Heap(A)`: Make the array a max-heap. Root is max.
2.  Swap $A[1]$ with $A[n]$ (Move max to end).
3.  Discard node $n$ from heap size.
4.  `Max-Heapify(A, 1)` to fix the new root.
5.  Repeat until heap size is 1.

**Running Time**: $O(n \lg n)$.

## 6.5 Priority Queues
Heaps are fantastic for implementing **Priority Queues**.
- `Insert(S, x)`: $O(\lg n)$
- `Maximum(S)`: $O(1)$
- `Extract-Max(S)`: $O(\lg n)$
- `Increase-Key(S, x, k)`: $O(\lg n)$

Used in process scheduling, Dijkstra's algorithm, and event simulation.
