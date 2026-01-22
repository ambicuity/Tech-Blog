---
layout: page
title: "AI Ch.5: Adversarial Search"
permalink: /courses/ai/ch5-adversarial-search/
---

# Chapter 5: Adversarial Search (Games)

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 5

When the environment includes another agent who is trying to defeat us (Zero-Sum Game).

## 5.1 Minimax Algorithm
- **MAX**: Our agent. Wants to maximize utility.
- **MIN**: Opponent. Wants to minimize utility.
- We assume MIN plays optimally.
- **Algorithm**: Recursively go down the tree. At leaf, return value. At MAX node, take `max` of children. At MIN node, take `min` of children.

## 5.2 Alpha-Beta Pruning
Minimax explores $O(b^m)$ nodes. We can ignore branches that definitely won't affect the decision.
- **$\alpha$**: Best value MAX typically can guarantee.
- **$\beta$**: Best value MIN can guarantee.
- If we find a move that is worse than a known alternative decision, stop looking at this branch.
- Reduces effective branching factor to $\sqrt{b}$.

## 5.3 Monte Carlo Tree Search (MCTS)
Used in **AlphaGo**.
Instead of looking at every move, run thousands of random simulations (playouts) to see who wins most often from current state.
1.  Selection
2.  Expansion
3.  Simulation (Rollout)
4.  Backpropagation
