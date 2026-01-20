---
layout: page
title: "DSA Ch.15: Dynamic Programming"
permalink: /courses/dsa/ch15-dynamic-programming/
---

# Chapter 15: Dynamic Programming

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 15

Dynamic Programming (DP) is a technique for solving problems by breaking them down into simpler subproblems and storing the results of these subproblems to avoid redundant computation.

It is applied to **Optimization Problems**.
Two key ingredients:
1.  **Optimal Substructure**: An optimal solution to the problem contains within it optimal solutions to subproblems.
2.  **Overlapping Subproblems**: The recursive algorithm visits the same subproblems repeatedly.

## 15.1 Rod Cutting
**Problem**: Given a rod of length $n$ and a table of prices $p_i$ for length $i$, determine the maximum revenue $r_n$ obtainable by cutting up the rod and selling the pieces.
- **Recursive**: $r_n = \max_{1 \le i \le n} (p_i + r_{n-i})$. Exponential time $2^n$.
- **DP (Memoization)**: Store results in an array. $O(n^2)$.

## 15.2 Matrix-Chain Multiplication
**Problem**: Given a sequence of $n$ matrices, parenthesize the product $A_1 A_2 \dots A_n$ to minimize the number of scalar multiplications.
- Order matters: $(A B) C$ vs $A (B C)$ costs differently.
- $O(n^3)$ using DP.

## 15.3 Elements of DP
- **Memoization (Top-Down)**: Write the recursive procedure, but cache the result.
- **Tabulation (Bottom-Up)**: Solve smallest subproblems first, fill up a table.

## 15.4 Longest Common Subsequence (LCS)
**Problem**: Given two sequences $X$ and $Y$, find the longest sequence that is a subsequence of both.
- Example: $X=\{A,B,C,B,D,A,B\}$, $Y=\{B,D,C,A,B,A\}$. $LCS=\{B,C,B,A\}$.
- **Recurrence**:
    - If $x_i == y_j$: $1 + LCS(i-1, j-1)$
    - Else: $\max(LCS(i-1, j), LCS(i, j-1))$
- Complexity: $\Theta(m \cdot n)$.
