---
layout: page
title: "Compilers Ch.9: Optimization"
permalink: /courses/compilers/ch9-optimization/
---

# Chapter 9: Machine-Independent Optimization

> **Reference**: *Compilers* (Dragon Book), Chapter 9

Improve code (speed/size) without changing meaning.

## 9.1 Local Optimization (Basic Blocks)
Linear sequence of code with one entry and exit.
- **Common Subexpression Elimination**: `a = b+c; d = b+c` -> `a = b+c; d = a`.
- **Dead Code Elimination**: Remove `x=1` if `x` is never used.
- **Constant Folding**: `x = 2*3` -> `x=6`.

## 9.2 Global Data Flow Analysis
Analyze flow of values across Control Flow Graph (CFG).
- **Reaching Definitions**: Which assignment `d: a=...` can reach point `p`?
- **Live Variable Analysis**: Is variable `x` needed in the future? (Used for Register Allocation).

## 9.3 Loop Optimization
Loops are where programs spend 90% of time.
- **Code Motion (Hoisting)**: Move invariant computation out of loop.
- **Induction Variable Elimination**: Replace multiplication with addition in arrays.
- **Loop Unrolling**: Decrease branch overhead.
