---
layout: page
title: "Compilers Ch.8: Code Generation"
permalink: /courses/compilers/ch8-code-generation/
---

# Chapter 8: Code Generation

> **Reference**: *Compilers* (Dragon Book), Chapter 8

Mapping IR to Assembly. Criteria: Correctness, Speed.

## 8.1 Instruction Selection
Mapping IR tree patterns to machine instructions.
-   `a = b + c`: `ADD R1, R2, R3`.
-   `a = a + 1`: `INC R1`.
-   **Tile Covering**: Cover the tree with tiles (instructions) to minimize cost.

## 8.2 Register Allocation
Registers are scarce.
**Graph Coloring Approach** (Chaitin).
1.  **Liveness Analysis**: Build interference graph. Nodes = Variables. Edge = Live at same time.
2.  **Coloring**: Color graph with $K$ colors ($K$ registers).
3.  **Spilling**: If $K$-coloring fails, spill variable to Stack (Memory).

## 8.3 Peephole Optimization
Scan generated assembly window (peephole).
-   Redundant Load/Store elimination.
-   Unreachable code.
-   Flow of control optimization.
