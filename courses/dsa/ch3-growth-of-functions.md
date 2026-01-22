---
layout: page
title: "DSA Ch.3: Growth of Functions"
permalink: /courses/dsa/ch3-growth-of-functions/
---

# Chapter 3: Growth of Functions

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 3

We drop lower-order terms and constants to focus on the rate of growth.

## 3.1 Asymptotic Notation
Definitions apply to functions $f(n), g(n)$ where domain is $\mathbb{N}$.

### $\Theta$-notation (Big-Theta)
Tight bound.
$$ \Theta(g(n)) = \{ f(n) : \exists c_1, c_2, n_0 \text{ such that } 0 \le c_1 g(n) \le f(n) \le c_2 g(n) \text{ for all } n \ge n_0 \} $$
*   "f(n) grows exactly as fast as g(n)".

### $O$-notation (Big-O)
Upper bound.
$$ O(g(n)) = \{ f(n) : \exists c, n_0 \text{ such that } 0 \le f(n) \le c g(n) \text{ for all } n \ge n_0 \} $$
*   "f(n) grows no faster than g(n)".
*   $f(n) = n^2 + 100 \implies f(n) \in O(n^2)$ and $f(n) \in O(n^3)$.

### $\Omega$-notation (Big-Omega)
Lower bound.
$$ \Omega(g(n)) = \{ f(n) : \exists c, n_0 \text{ such that } 0 \le c g(n) \le f(n) \text{ for all } n \ge n_0 \} $$
*   "f(n) grows at least as fast as g(n)".

---

## 3.2 Standard Notations
-   **Monotonicity**: $f(n) \le f(n+1)$.
-   **Floors/Ceilings**: $\lfloor x \rfloor, \lceil x \rceil$.
-   **Logarithms**: $\lg n = \log_2 n$, $\ln n = \log_e n$.
-   **Factorials**: $n! \approx \sqrt{2\pi n} (\frac{n}{e})^n$ (Stirling's approx). $\lg (n!) = \Theta(n \lg n)$.

## 3.3 Common Growth Rates
$$ 1 < \lg n < \sqrt{n} < n < n \lg n < n^2 < n^3 < 2^n < n! $$
