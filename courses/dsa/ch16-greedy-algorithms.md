---
layout: page
title: "DSA Ch.16: Greedy Algorithms"
permalink: /courses/dsa/ch16-greedy-algorithms/
---

# Chapter 16: Greedy Algorithms

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 16

Algorithms for optimization problems typically go through a sequence of steps, with a set of choices at each step. A **greedy algorithm** always makes the choice that looks best at the moment.

Properties:
1.  **Greedy-Choice Property**: A global optimal solution can be arrived at by making a locally optimal (greedy) choice.
2.  **Optimal Substructure**: Same as DP.

## 16.1 An Activity-Selection Problem
**Problem**: Given a set of activities with start time $s_i$ and finish time $f_i$, select the maximum number of mutually compatible activites.
- **Greedy Strategy**: Always pick the activity that **finishes earliest**. This leaves maximum resource for subsequent activities.
- Complexity: $\Theta(n \lg n)$ (sorting by finish time).

## 16.2 Elements of the Greedy Strategy
**Greedy vs Dynamic Programming**:
- **0-1 Knapsack Problem**: A thief has a knapsack of capacity $W$. Items have value $v_i$ and weight $w_i$. Can take item or leave it.
    - Greedy fails. Must use DP.
- **Fractional Knapsack Problem**: Can take a fraction of an item (e.g., gold dust).
    - Greedy works (Take item with highest value/weight ratio).

## 16.3 Huffman Codes
Used for data compression (e.g., in PKZIP/JPEG).
- Idea: Use short binary codes for frequent characters, long codes for rare characters.
- **Prefix Codes**: No code involves the prefix of another (prevents ambiguity).
- **Algorithm**: Build a binary tree bottom-up. Merge two nodes with lowest frequency. $O(n \lg n)$.
