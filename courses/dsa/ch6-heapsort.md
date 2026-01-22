---
layout: page
title: "DSA Ch.6: Heapsort"
permalink: /courses/dsa/ch6-heapsort/
---

# Chapter 6: Heapsort

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 6

Introduces the **Heap** data structure. Steps:
1.  Build Heap.
2.  Extract Max.

## 6.1 Heaps
A nearly complete binary tree.
-   **Max-Heap Property**: $A[Parent(i)] \ge A[i]$.
-   **Indices**:
    -   $Parent(i) = \lfloor i/2 \rfloor$.
    -   $Left(i) = 2i$.
    -   $Right(i) = 2i+1$.

## 6.2 Maintaining the Heap
`Max-Heapify(A, i)`: Assumes Left(i) and Right(i) are heaps, but A[i] might be small. Floats A[i] down.
-   Time: $O(\lg n)$ (Height of tree).

## 6.3 Building a Heap
`Build-Max-Heap(A)`:
Run `Max-Heapify` on all non-leaf nodes ($\lfloor n/2 \rfloor$ down to 1).
-   **Analysis**: While it looks like $O(n \lg n)$, a tighter analysis shows it is **$O(n)$**. (Most nodes are at bottom with height 1, few at top).

## 6.4 The Heapsort Algorithm
1.  `Build-Max-Heap(A)`.
2.  Swap $A[1]$ with $A[n]$. Decrease heap size.
3.  `Max-Heapify(A, 1)`.
4.  Repeat.

Total Time: $O(n \lg n)$.
-   **Pros**: Sorted in place (unlike Merge Sort).
-   **Cons**: Not stable, poor cache locality compared to Quicksort.

## 6.5 Priority Queues
Heaps are mostly used for PQs.
-   `Insert(S, x)`: Place at end, float up ($O(\lg n)$).
-   `Extract-Max(S)`: Return root, swap last to root, float down ($O(\lg n)$).
