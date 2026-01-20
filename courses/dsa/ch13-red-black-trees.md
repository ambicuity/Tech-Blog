---
layout: page
title: "DSA Ch.13: Red-Black Trees"
permalink: /courses/dsa/ch13-red-black-trees/
---

# Chapter 13: Red-Black Trees

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 13

A Red-Black tree is a binary search tree with one extra bit of storage per node: its **color** (RED or BLACK). By constraining the node colors on any path, we ensure that no path is more than twice as long as any other, so the tree is approximately balanced.

## 13.1 Properties
1.  Every node is either red or black.
2.  The root is black.
3.  Every leaf (NIL) is black.
4.  If a node is red, then both its children are black. (No two Reds in a row).
5.  For each node, all simple paths from the node to descendant leaves contain the same number of black nodes (**Black-Height**).

**Result**: Height $h \le 2 \lg(n+1)$. Complexity of essential operations is guaranteed $O(\lg n)$.

## 13.2 Rotations
Operations that change local structure but preserve the BST property. Used during insertion/deletion to fix color violations.
- **Left-Rotate(T, x)**: Pivot `x` down to left, pull `x.right` up.
- **Right-Rotate(T, y)**: Pivot `y` down to right, pull `y.left` up.
- Time: $O(1)$.

## 13.3 Insertion
Insert node $z$ as usual and color it **RED**.
- Violation: If parent is also RED (Property 4).
- **Fixup**:
    - Case 1: Uncle is active RED. Recolor Parent/Uncle BLACK, Grandparent RED. Move up.
    - Case 2: Uncle is BLACK, $z$ is "inner" child. Rotation to make it Case 3.
    - Case 3: Uncle is BLACK, $z$ is "outer" child. Rotation + Recolor.

## 13.4 Deletion
Standard BST deletion, but track the color of the removed node $y$. If $y$ was BLACK, we might have violated black-height. We add an "extra black" to $x$ and push it up the tree until balanced.
