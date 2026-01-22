---
layout: page
title: "DSA Ch.8: Linear Sort"
permalink: /courses/dsa/ch8-linear-sort/
---

# Chapter 8: Sorting in Linear Time

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 8

**Lower Bound**: Any comparison-based sort (Merge, Heap, Quick) requires $\Omega(n \lg n)$ comparisons.
To beat this, we must stop comparing and start **Counting**.

## 8.1 Counting Sort
Assumption: Input integers are in range $0 \dots k$.
1.  Create array `C[0..k]`.
2.  Count occurrences: `C[A[i]]++`.
3.  Cumulative sum `C` to find positions.
4.  Place elements.
-   **Time**: $O(n + k)$.
-   **Space**: $O(k)$. Stable.

## 8.2 Radix Sort
Sorts numbers digit by digit (Least Significant Digit first).
Requires a stable intermediate sort (like Counting Sort).
-   If we have $d$ digits, cost is $O(d(n+k))$.
-   Can sort integers up to $N^2$ in linear time $O(N)$ by treating them as base-$N$ numbers ($d=2$).

## 8.3 Bucket Sort
Assumption: Input uniformly distributed over $[0, 1)$.
1.  Divide $[0, 1)$ into $n$ equal buckets.
2.  Scatter $A[i]$ into buckets.
3.  Sort buckets (Insertion Sort).
4.  Concat.
-   Expected time $O(n)$.
