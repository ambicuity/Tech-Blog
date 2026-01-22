---
layout: page
title: "AI Ch.4: Complex Search"
permalink: /courses/ai/ch4-complex-search/
---

# Chapter 4: Search in Complex Environments

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 4

What if we want to search where we don't care about the *path*, only the *result* (e.g., N-Queens board)?

## 4.1 Local Search
Keep a single "current" state and try to improve it.
- **Hill Climbing**: Move to best neighbor.
    - Problem: Local Maxima (getting stuck on a small hill but missing Everest).
- **Simulated Annealing**: Allow bad moves occasionally to escape local maxima.
    - High "Temperature" $T$: accept bad moves. Lower $T$ gradually.

## 4.2 Genetic Algorithms
Inspired by evolution.
1.  **Population**: Start with $k$ random states.
2.  **Fitness Function**: Score each state.
3.  **Selection**: Pick best parents.
4.  **Crossover**: Combine parts of two parents.
5.  **Mutation**: Randomly flip bits.

## 4.3 Search with Nondeterminism
If the environment is slippery (I try to move Forward, but 10% chance I slip Right).
- Result is a **Contingency Plan** (Tree), not a sequence. "If clean, then Left. If dirty, then Suck".
- **AND-OR Search Trees**.
