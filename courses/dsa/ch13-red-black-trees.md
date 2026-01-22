---
layout: page
title: "DSA Ch.13: Red-Black Trees"
permalink: /courses/dsa/ch13-red-black-trees/
---

# Chapter 13: Red-Black Trees

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 13

A **Balanced** BST. Height guaranteed to be $O(\lg n)$.

## 13.1 RB Properties
1.  Every node is Red or Black.
2.  Root is Black.
3.  Leaves (NIL) are Black.
4.  If a node is Red, both children are Black (No Red-Red edges).
5.  For each node, all paths to descendant leaves contain same number of Black nodes (**Black-Height**).

**Height Bound**: $h \le 2 \lg(n+1)$.

## 13.2 Rotations
Local operations to restructure tree while preserving BST property. $O(1)$.
-   `Left-Rotate(x)`: Moves x down, x.right up.
-   `Right-Rotate(y)`: Moves y down, y.left up.

## 13.3 Insertion
Insert red node $z$. Fix violations (Red-Red).
**Case 1**: Uncle is Red. Color Flip (Parent/Uncle $\to$ Black, Grandparent $\to$ Red). Move up.
**Case 2**: Uncle is Black, Triangle. Rotate to Line.
**Case 3**: Uncle is Black, Line. Rotate + Recolor. Done.

## 13.4 Deletion
Complex. Requires fixing "Double Black" nodes.
