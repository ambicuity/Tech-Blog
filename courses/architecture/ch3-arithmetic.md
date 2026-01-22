---
layout: page
title: "Arch Ch.3: Arithmetic"
permalink: /courses/architecture/ch3-arithmetic/
---

# Chapter 3: Arithmetic for Computers

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 3

Computers manipulate binary numbers. A 32-bit word is just a string of 0s and 1s.

## 3.1 Signed Numbers
How to represent negative numbers?
- **Sign-Magnitude**: First bit is sign. Problem: Two zeros (+0, -0). Hard hardware.
- **2's Complement**: Leading system.
    - To negate: Invert bits and add 1.
    - Range: $-2^{n-1}$ to $2^{n-1}-1$.
    - Addition works exactly the same for signed and unsigned!

## 3.2 Addition and Subtraction
- **ALU (Arithmetic Logic Unit)**: Hardware block.
- **Overflow**: Result is too large to fit in 32 bits.
    - On addition: Occurs if operands have same sign, but result has different sign.

## 3.3 Multiplication
- **Grade School Algorithm**: Shift and add.
- **Hardware**: Implementation involves a 64-bit product register.
- **Fast Multiplication**: Booth's Algorithm (handles signed numbers properly).

## 3.4 Floating Point (IEEE 754)
Representation for Reals (Scientific notation: $1.xxxx \times 2^{yyyy}$).
- **Single Precision (32-bit)**:
    - Sign (1 bit).
    - Exponent (8 bits): Bias-127.
    - Significand (23 bits).
- **Double Precision (64-bit)**:
    - Exponent (11 bits).
    - Significand (52 bits).
- Special values: `+Infinity`, `-Infinity`, `NaN` (Not a Number).
