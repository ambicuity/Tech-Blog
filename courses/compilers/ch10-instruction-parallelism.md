---
layout: page
title: "Compilers Ch.10: Parallelism"
permalink: /courses/compilers/ch10-instruction-parallelism/
---

# Chapter 10: Instruction-Level Parallelism

> **Reference**: *Compilers* (Dragon Book), Chapter 10

How can the compiler reorganize code to exploit hardware parallelism (Pipelining, Superscalar, VLIW)?

## 10.1 Data Dependence
- **True Dependence (Read-after-Write)**:
    - `a = 1; b = a;` (b depends on a). Cannot reorder.
- **Anti-Dependence (Write-after-Read)**:
    - `b = a; a = 1;`
- **Output Dependence (Write-after-Write)**:
    - `a = 1; a = 2;`

## 10.2 Basic Block Scheduling
- Construct **Data Dependence Graph**.
- **List Scheduling**: Greedy algorithm. Pick instruction whose predecessors are done and minimizes stall.

## 10.3 Global Scheduling
- Moving instructions across basic blocks.
- **Trace Scheduling**: Optimize the most frequent path (trace). Add compensation code for off-trace paths.

## 10.4 Software Pipelining
Optimization for loops. Assume loop body is "unrolled".
- Overlap iteration $i$ with iteration $i+1$.
- **Modulo Scheduling**: Schedule instructions modulo $II$ (Initiation Interval).
