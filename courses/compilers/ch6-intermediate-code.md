---
layout: page
title: "Compilers Ch.6: Intermediate Code"
permalink: /courses/compilers/ch6-intermediate-code/
---

# Chapter 6: Intermediate Code Generation

> **Reference**: *Compilers* (Dragon Book), Chapter 6

We translate the AST into a machine-independent low-level representation.
Benefits: Portability (Frontend for C++, Backend for x86 / Backend for ARM). Ease of optimization.

## 6.1 Three-Address Code (TAC)
Instructions with at most three operands.
`x = y op z`
- `t1 = b * c`
- `t2 = a + t1`
- `t3 = d * e`
- `t4 = t2 + t3`

## 6.2 Implementation
- **Quadruples**: Record with fields `(op, arg1, arg2, result)`.
- **Triples**: `(op, arg1, arg2)`. Result is referred to by index.

## 6.3 Translating Control Flow
- **If-Then-Else**:
```
if (B) S1 else S2
```
becomes:
```
    if B goto L1
    goto L2
L1: code for S1
    goto L3
L2: code for S2
L3: ...
```
- **Backpatching**: Generating jumps with empty targets and filling them in later when label addresses are known.
