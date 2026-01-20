---
layout: page
title: "DSA Ch.3: Growth of Functions"
permalink: /courses/dsa/ch3-growth-of-functions/
---

# Chapter 3: Growth of Functions

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 3

The order of growth of the running time of an algorithm gives a simple characterization of the algorithm's efficiency and also allows us to compare the relative performance of alternative algorithms.

## 3.1 Asymptotic Notation
We use asymptotic notation to describe the running time of an algorithm for **large inputs**.

### 1. Theta Notation ($\Theta$-notation)
Depending on inputs, the exact running time may vary. $\Theta(g(n))$ represents the **exact** asymptotic bound.
> $f(n) = \Theta(g(n))$ if there exist positive constants $c_1, c_2, n_0$ such that $0 \le c_1 g(n) \le f(n) \le c_2 g(n)$ for all $n \ge n_0$.

**Intuition**: $f(n)$ is "sandwiched" between $c_1 g(n)$ and $c_2 g(n)$.

### 2. O-Notation ($O$-notation)
Represents an **asymptotic upper bound**. We use it to bound the **worst-case** running time.
> $f(n) = O(g(n))$ if there exist positive constants $c, n_0$ such that $0 \le f(n) \le c g(n)$ for all $n \ge n_0$.

### 3. Omega Notation ($\Omega$-notation)
Represents an **asymptotic lower bound**.
> $f(n) = \Omega(g(n))$ if there exist positive constants $c, n_0$ such that $0 \le c g(n) \le f(n)$ for all $n \ge n_0$.

## 3.2 Standard Notations and Common Functions
- **Monotonicity**: A function $f(n)$ is monotonically increasing if $m \le n$ implies $f(m) \le f(n)$.
- **Polynomials**: An asymptotically positive polynomial $p(n)$ of degree $d$ is $\Theta(n^d)$.
- **Exponentials**: For all real constants $a > 1$ and $b > 1$, $\lim_{n \to \infty} \frac{n^b}{a^n} = 0$ (exponentials beat polynomials).
- **Logarithms**: We define $\lg n = \log_2 n$ (binary logarithm), $\ln n = \log_e n$ (natural logarithm).

**Ranking of Common complexities**:
$O(1) < O(\lg n) < O(n) < O(n \lg n) < O(n^2) < O(2^n) < O(n!)$
