---
layout: page
title: "Arch Ch.3: Arithmetic"
permalink: /courses/architecture/ch3-arithmetic/
---

# Chapter 3: Arithmetic for Computers

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 3

ALU Design.

## 3.1 Integer Arithmetic
-   **Addition**: Full Adder ($Sum = A \oplus B \oplus Cin$, $Cout = AB + Cin(A \oplus B)$). Ripple Carry vs Carry Lookahead (CLA).
-   **Multiplication**: Shift and Add. Optimized Booth's Algorithm for signed numbers.

## 3.2 Floating Point (IEEE 754)
Representation of reals.
$$ (-1)^S \times (1 + Fraction) \times 2^{(Exponent - Bias)} $$
**Single Precision (32-bit)**:
-   S (1 bit).
-   Exponent (8 bits, Bias 127).
-   Fraction (23 bits).

**Issues**:
-   **Overflow**: Too large.
-   **Underflow**: Too small (use subnormals).
-   **Precision**: $0.1 + 0.2 \neq 0.3$.
