---
layout: page
title: "DSA Ch.4: Divide-and-Conquer"
permalink: /courses/dsa/ch4-divide-and-conquer/
---

# Chapter 4: Divide-and-Conquer

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 4

The **divide-and-conquer** paradigm involves three steps at each level of the recursion:
1.  **Divide** the problem into a number of subproblems that are smaller instances of the same problem.
2.  **Conquer** the subproblems by solving them recursively. If the subproblem sizes are small enough (base case), solve them directly.
3.  **Combine** the solutions to the subproblems into the solution for the original problem.

## 4.1 The Maximum-Subarray Problem
**Problem**: You are given an array of prices for a stock over a period of time. Find the contiguous subarray of days that yields the maximum profit (buy low, sell high).
- **Brute Force**: Check all $\Theta(n^2)$ pairs.
- **Divide-and-Conquer**: $\Theta(n \lg n)$.
    - Divide array into two halves.
    - Max subarray must be in left half, right half, or crossing the midpoint.
    - Solve recursively.

## 4.2 Strassen's Algorithm for Matrix Multiplication
Multiplying two $n \times n$ matrices.
- **Naïve Algorithm**: $\Theta(n^3)$ (Three nested loops).
- **Strassen's Algorithm**: $\Theta(n^{\lg 7}) \approx O(n^{2.81})$.
    - Uses a clever algebraic trick to reduce 8 recursive multiplications to 7.

## 4.3 The Master Method
A "cookbook" method for solving recurrences of the form:
$$T(n) = aT(n/b) + f(n)$$
where $a \ge 1$ and $b > 1$.

compare $f(n)$ with $n^{\log_b a}$:

1.  **Case 1**: If $f(n) = O(n^{\log_b a - \epsilon})$ (polynomially smaller), then $T(n) = \Theta(n^{\log_b a})$.
2.  **Case 2**: If $f(n) = \Theta(n^{\log_b a})$, then $T(n) = \Theta(n^{\log_b a} \lg n)$.
3.  **Case 3**: If $f(n) = \Omega(n^{\log_b a + \epsilon})$ (polynomially larger), and regularity condition holds, then $T(n) = \Theta(f(n))$.

**Example (Merge Sort)**:
$T(n) = 2T(n/2) + \Theta(n)$.
$a=2, b=2 \implies n^{\log_2 2} = n^1 = n$.
$f(n) = \Theta(n)$, so Case 2 applies.
$T(n) = \Theta(n \lg n)$.
