---
layout: page
title: "DSA Ch.7: Quicksort"
permalink: /courses/dsa/ch7-quicksort/
---

# Chapter 7: Quicksort

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 7

The practical sorting champion.

## 7.1 Description
Divide-and-Conquer, but does work in the **Divide** step (Partitioning).
`Quicksort(A, p, r)`:
1.  `q = Partition(A, p, r)`
2.  `Quicksort(A, p, q-1)`
3.  `Quicksort(A, q+1, r)`

## 7.2 Partitioning
Lomuto Partition scheme:
-   Pivot $x = A[r]$.
-   Maintain index $i$ ending the "smaller than x" region.
-   Scan $j$ from $p$ to $r-1$. If $A[j] \le x$, increment $i$, swap $A[i], A[j]$.
-   Swap pivot to $i+1$.

## 7.3 Performance
-   **Worst Case**: $O(n^2)$. Happens if pivot is always min or max (e.g. sorted array).
-   **Best Case**: $O(n \lg n)$. Pivot always splits 50/50.
-   **Average Case**: $O(n \lg n)$. Even a 9-to-1 split yields logarithmic depth.

## 7.4 Randomized Quicksort
Pick a random element as pivot.
-   Guarantees expected $O(n \lg n)$ time regardless of input distribution.
-   No input causes worst-case behavior. The coin flips must be unlucky.
