---
layout: page
title: "DSA Ch.5: Probabilistic Analysis"
permalink: /courses/dsa/ch5-probabilistic-analysis/
---

# Chapter 5: Probabilistic Analysis and Randomized Algorithms

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 5

Sometimes, we can't guarantee worst-case performance, or we want to make the worst-case extremely unlikely by using randomness.

## 5.1 The Hiring Problem
You interview candidates one by one. If better than current best, hire them.
**Cost**: Interview is cheap. Hiring is expensive (fire old, hire new).
Worst case: Candidates sorted increasing quality ($N$ hirings).

**Randomized Algorithm**: Shuffle the candidates first.
Expected hirings: $\ln N$.
*   Why? Candidate $i$ is hired only if they are the best of the first $i$. Prob = $1/i$.
*   $\sum_{i=1}^N 1/i = \ln N$.

## 5.2 Indicator Random Variables
A powerful tool for analysis.
$X_A = I\{A\}$. 1 if event A happens, 0 if not.
$E[X_A] = P(A)$.
Expected total count $X = \sum X_i$. linearity of expectation applies even if not independent.

## 5.3 Randomized Quicksort
Instead of picking first element as pivot, pick random.
Worst case still $O(N^2)$, but probability vanishes.
Expected time: $O(N \log N)$ for *any* input.

---

## 5.4 Skip Lists
A randomized data structure.
Linked list with "express lanes".
Search/Insert/Delete: $O(\log N)$ expected.
Alternative to balanced trees.
