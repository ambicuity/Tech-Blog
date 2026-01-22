---
layout: page
title: "DSA Ch.9: Medians"
permalink: /courses/dsa/ch9-medians/
---

# Chapter 9: Medians and Order Statistics

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 9

**Selection Problem**: Find the $i$-th smallest element in a set of $n$ distinct numbers.
-   $i=1$: Minimum.
-   $i=n$: Maximum.
-   $i= \lfloor (n+1)/2 \rfloor$: **Median**.

## 9.1 Simple Solutions
-   **Sorting**: Sort the array ($O(n \log n)$), then return $A[i]$.
    -   Can we do better? Yes, $O(n)$.

## 9.2 Minimum and Maximum
-   **Minimum**: $n-1$ comparisons.
-   **Min and Max**: We can do it in $3 \lfloor n/2 \rfloor$ comparisons.
    -   Process elements in pairs. Compare pair ($a, b$). Compare smaller with current min, larger with current max.

## 9.3 Selection in Linear Time (Randomized Select)
Modeled after Quicksort.
`Randomized-Select(A, p, r, i)`:
1.  If $p=r$, return $A[p]$.
2.  $q = \text{Randomized-Partition}(A, p, r)$. (Returns pivot index).
3.  $k = q - p + 1$. (Number of elements in low side).
4.  If $i == k$, return $A[q]$ (Pivot is the answer).
5.  If $i < k$, recurse on Left: `Randomized-Select(A, p, q-1, i)`.
6.  If $i > k$, recurse on Right: `Randomized-Select(A, q+1, r, i-k)`.

**Analysis**:
-   Worst Case: $O(n^2)$ (bad pivots).
-   **Expected Time**: $O(n)$.

## 9.4 Selection in Worst-Case Linear Time
"Median of Medians" algorithm.
1.  Divide n elements into $\lfloor n/5 \rfloor$ groups of 5.
2.  Find median of each group.
3.  Recursively find median $x$ of the medians.
4.  Use $x$ as pivot for Partition.
-   Guarantees a good split (30%/70%).
-   $T(n) = T(n/5) + T(7n/10) + O(n)$.
-   Solution: $O(n)$.
