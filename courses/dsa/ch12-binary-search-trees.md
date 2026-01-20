---
layout: page
title: "DSA Ch.12: BST"
permalink: /courses/dsa/ch12-binary-search-trees/
---

# Chapter 12: Binary Search Trees

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 12

Search trees are data structures that support many dynamic-set operations, including `Search`, `Minimum`, `Maximum`, `Predecessor`, `Successor`, `Insert`, and `Delete`.

## 12.1 What is a BST?
A binary search tree is a binary tree where each node `x` satisfies the **binary-search-tree property**:
- If `y` is a node in the left subtree of `x`, then `y.key` $\le$ `x.key`.
- If `y` is a node in the right subtree of `x`, then `y.key` $\ge$ `x.key`.

**Inorder Tree Walk**: Prints keys in sorted order. $\Theta(n)$.

## 12.2 Querying a BST
- **Search**: Trace a path from root. If $k < x.key$, go left. Else go right.
- **Minimum**: Go left until you hit a leaf.
- **Maximum**: Go right until you hit a leaf.
- **Successor**: The node with the smallest key greater than `x.key`.
    - If right subtree is non-empty: Minimum of right subtree.
    - Else: Use parent pointer to go up until you turn right.

**Complexity**: All operations are $O(h)$, where $h$ is height of tree.

## 12.3 Insertion and Deletion
- **Insertion**: Like search. When you hit a `NIL`, place new node there.
- **Deletion**:
    - Case 1: Node $z$ has no children. Just remove it.
    - Case 2: Node $z$ has one child. Splice $z$ out.
    - Case 3: Node $z$ has two children. Find $z$'s successor $y$ (which has no left child). Splice $y$ out, and replace $z$ with $y$.

## 12.4 Randomly Built BSTs
If we insert $n$ keys in random order, expected height is $O(\lg n)$.
If we insert sorted keys, height is $O(n)$ (Linked list).
To guarantee $O(\lg n)$, we need **Balanced Trees** (e.g., Red-Black Trees).
