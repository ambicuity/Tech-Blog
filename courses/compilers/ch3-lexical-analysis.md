---
layout: page
title: "Compilers Ch.3: Lexical Analysis"
permalink: /courses/compilers/ch3-lexical-analysis/
---

# Chapter 3: Lexical Analysis

> **Reference**: *Compilers* (Dragon Book), Chapter 3

## 3.1 RegEx to NFA (Thompson's Construction)
Inductive construction.
-   **a**: Start -> (a) -> End.
-   **AB**: Link End(A) to Start(B).
-   **A|B**: New Start split to Start(A), Start(B).
-   **A***: Loop back.

## 3.2 NFA to DFA (Subset Construction)
Simulate NFA. Each state in DFA corresponds to a **Set** of NFA states.
-   `$\epsilon$-closure(S)`: All states reachable from S on $\epsilon$.
-   `move(T, a)`: All states reachable from set T on input 'a'.
-   Next State = `$\epsilon$-closure(move(T, a))`.

## 3.3 DFA Minimization
Hopcroft's Algorithm. Partition states into groups. Distinguishable if they lead to different outcomes (Accept vs Reject) on some string.
