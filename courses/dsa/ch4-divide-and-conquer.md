---
layout: page
title: "DSA Ch.4: Divide-and-Conquer"
permalink: /courses/dsa/ch4-divide-and-conquer/
---

# Chapter 4: Divide-and-Conquer

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 4

Recursive algorithms often follow this pattern. We solve recurrences to find complexity.

## 4.1 The Maximum Subarray Problem
Given array of price changes, find contiguous subarray with largest sum.
-   **Brute Force**: Check all $\Theta(n^2)$ pairs.
-   **Divide & Conquer**:
    -   Max subarray is either in Left, Right, or Crossing the midpoint.
    -   $T(n) = 2T(n/2) + \Theta(n) \implies \Theta(n \lg n)$.
-   **Kadane's Algorithm**: $O(n)$ (Dynamic Programming).

## 4.2 Strassen's Algorithm for Matrix Multiplication
Standard Matrix Mult is $\Theta(n^3)$.
Strassen found a way to compute $2 \times 2$ product with only **7 multiplications** (instead of 8).
$$ T(n) = 7 T(n/2) + \Theta(n^2) $$
$$ T(n) = \Theta(n^{\log_2 7}) \approx \Theta(n^{2.81}) $$

---

## 4.3 The Master Method
For recurrences of form $T(n) = a T(n/b) + f(n)$.
Compare $f(n)$ to $n^{\log_b a}$ (the "watershed" function).

1.  **Case 1**: If $f(n) = O(n^{\log_b a - \epsilon})$, then $T(n) = \Theta(n^{\log_b a})$. (Cost dominated by leaves).
2.  **Case 2**: If $f(n) = \Theta(n^{\log_b a})$, then $T(n) = \Theta(n^{\log_b a} \lg n)$. (Cost evenly distributed).
3.  **Case 3**: If $f(n) = \Omega(n^{\log_b a + \epsilon})$ and regularity holds, then $T(n) = \Theta(f(n))$. (Cost dominated by root).

### Examples
-   **Merge Sort**: $a=2, b=2, f(n)=n$. $n^{\log_2 2} = n^1$. Case 2. $\Theta(n \lg n)$.
-   **Binary Search**: $a=1, b=2, f(n)=1$. $n^{\log_2 1} = n^0 = 1$. Case 2. $\Theta(\lg n)$.
