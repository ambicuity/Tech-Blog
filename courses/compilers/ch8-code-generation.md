---
layout: page
title: "Compilers Ch.8: Code Gen"
permalink: /courses/compilers/ch8-code-generation/
---

# Chapter 8: Code Generation

> **Reference**: *Compilers* (Dragon Book), Chapter 8

The final phase. Map IR to target Machine Code (x86 Assembly).
Goals: Correctness, Efficiency.

## 8.1 Instruction Selection
Mapping IR `t = a + b` to:
```asm
MOV R1, a
ADD R1, b
MOV t, R1
```
- Or `INC a` if `b=1`.
- Can be modeled as **Tree Covering** problem.

## 8.2 Register Allocation
Registers are fast but scarce.
- **Graph Coloring**:
    - Construct **Interference Graph**. Nodes are variables. Edge if they are "live" at the same time.
    - If graph is K-colorable (K = num registers), we can assign registers without spilling.
    - If not, **Spill** variable to stack (load/store cost).

## 8.3 Instruction Scheduling
Reorder instructions to avoid pipeline stalls.
- If `LOAD` takes 3 cycles, put independent instructions immediately after it.
