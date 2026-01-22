---
layout: page
title: "AI Ch.3: Solving Problems by Search"
permalink: /courses/ai/ch3-search/
---

# Chapter 3: Solving Problems by Searching

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 3

When the correct action is not immediately obvious, an agent must **search** for a sequence of actions that reaches the goal.

## 3.1 Problem Formulation
- **Initial State**: Where we start.
- **Actions**: `Actions(s)` returns set of actions available in state `s`.
- **Transition Model**: `Result(s, a)` returns state after doing `a` in `s`.
- **Goal Test**: Are we there yet?
- **Path Cost**: Sum of costs (usually distance/time).

## 3.2 Uninformed Search Strategies (Blind Search)
No information about how close we are to goal.
1.  **Breadth-First Search (BFS)**: Expand shallowest nodes first. (FIFO Queue).
    - Optimal (if cost=1), Complete.
    - **Space Complexity**: $O(b^d)$. Exponential memory usage is the killer.
2.  **Depth-First Search (DFS)**: Expand deepest nodes first. (LIFO / Recursion).
    - Efficient space $O(bm)$. Not optimal. Not complete (can get stuck in loops).
3.  **Iterative Deepening Search (IDS)**: Run DFS with limit 1, then limit 2, etc.
    - Best of both worlds: $O(bd)$ time, $O(bd)$ space.

## 3.3 Informed (Heuristic) Search Strategies
Use knowledge ($h(n)$) to guide search.
- **Heuristic $h(n)$**: Estimated cost from node $n$ to goal.
- **Greedy Best-First Search**: Expand node with lowest $h(n)$. (Like a moth to a flame). Not optimal.
- **A* Search (A-Star)**: Expand node with lowest $f(n) = g(n) + h(n)$.
    - $g(n)$: Actual cost to reach $n$.
    - $h(n)$: Estimated cost to goal.
    - **Optimality**: If $h(n)$ is **admissible** (never overestimates cost), A* is optimal.
