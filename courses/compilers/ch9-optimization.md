---
layout: page
title: "Compilers Ch.9: Optimization"
permalink: /courses/compilers/ch9-optimization/
---

# Chapter 9: Machine-Independent Optimization

> **Reference**: *Compilers* (Dragon Book), Chapter 9

Optimization transforms code to make it faster or smaller, while preserving semantics. The compiler builds a **Control Flow Graph (CFG)** where nodes are Basic Blocks and edges are jumps.

## 9.1 Data Flow Analysis
We simulate the execution of the program for all possible paths to gather static information.

### 1. Reaching Definitions
*   **Goal**: For each point in the program, determine which definitions (`d: x = ...`) *may* reach that point without being overwritten.
*   **Equation**:
    $$ OUT[B] = gen_B \cup (IN[B] - kill_B) $$
    $$ IN[B] = \bigcup_{P \in pred(B)} OUT[P] $$
*   **Algorithm**: Iterative Fixed-Point Algorithm. Initialize, then repeat until no set changes.
*   **Application**: Constant Propagation, Loop Invariant Code Motion.

### 2. Live Variable Analysis
*   **Goal**: Determine if variable `x` holds a value that *may* be used in the future.
*   **Equation** (Backward Flow):
    $$ IN[B] = use_B \cup (OUT[B] - def_B) $$
    $$ OUT[B] = \bigcup_{S \in succ(B)} IN[S] $$
*   **Application**: Dead Code Elimination (if `x` is not live after assignment, remove assignment). Register Allocation (if `x` and `y` are live at same time, they interfere).

---

## 9.2 Loop Optimizations
Since 90% of time is spent in loops, we focus here.

### 1. Loop Invariant Code Motion (Hoisting)
If `t = x + y` is inside a loop, but `x` and `y` do not change inside the loop, move `t = x + y` to the pre-header.

### 2. Induction Variable Elimination
```c
// Before
for (i=0; i<100; i++) {
    offset = 4 * i;   // Multiplication is expensive
    x = A[offset];
}
```
```c
// After (Strength Reduction)
offset = 0;
for (i=0; i<100; i++) {
    x = A[offset];
    offset = offset + 4; // Addition is cheap
}
```

## 9.3 Global Common Subexpression Elimination
If `a = b + c` is calculated in Block 1, and Block 2 calculates `d = b + c`, and `b, c` haven't changed:
-   Replace calculation in Block 2 with usage of `a`.

---

## 9.4 SSA Form (Static Single Assignment)
A modern IR where every variable is assigned exactly **once**.
-   `x = 1; x = 2;` becomes `x_1 = 1; x_2 = 2;`.
-   **Phi Functions ($\phi$)**: Used at merge points (joins in CFG). `x_3 = \phi(x_1, x_2)`.
-   Simplifies many optimizations (Constant Propagation becomes trivial).
