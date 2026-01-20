---
layout: page
title: "DSA Ch.8: Linear Sort"
permalink: /courses/dsa/ch8-linear-sort/
---

# Chapter 8: Sorting in Linear Time

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 8

We have established a lower bound of $\Omega(n \lg n)$ for **comparison sorts** (Heapsort, Merge Sort, Quicksort). To sort faster, we must assume something about the input and avoid comparing elements directly.

## 8.1 Lower Bounds for Sorting
Any decision tree that sorts $n$ elements must have height $\Omega(n \lg n)$. Thus, no comparison sort can be faster than $O(n \lg n)$.

## 8.2 Counting Sort
Assumes input elements are integers in the range $0$ to $k$.
- **Idea**: Count how many elements are equal to $x$. Use this to place $x$ directly into its position.
- **Time**: $\Theta(n+k)$.
- **Space**: $\Theta(n+k)$.
- **Stable**: Yes. (Crucial for Radix sort).

## 8.3 Radix Sort
Sorts on the least significant digit first using a stable sort (like Counting Sort).
- **Time**: $\Theta(d(n+k))$ where $d$ is number of digits.
- Historic use: Sorting punch cards.

## 8.4 Bucket Sort
Assumes input is drawn from a uniform distribution over $[0, 1)$.
- **Idea**: Divide interval $[0, 1)$ into $n$ equal-sized buckets. Distribute $n$ inputs into buckets. Sort each bucket (usually Insertion Sort). Concatenate.
- **Expected Time**: $\Theta(n)$.
