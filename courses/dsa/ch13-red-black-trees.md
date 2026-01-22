---
layout: page
title: "DSA Ch.13: Red-Black Trees"
permalink: /courses/dsa/ch13-red-black-trees/
---

# Chapter 13: Red-Black Trees

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 13

Full RBT implementation includes extensive case handling (300+ lines). Here is the critical **Left Rotate** logic.

## 13.1 Left Rotate
Moves `x` down to left, moves `y` (right child) up.

```python
class Node:
    def __init__(self, data, color="RED"):
        self.data = data
        self.color = color 
        self.left = None
        self.right = None
        self.parent = None

def left_rotate(tree, x):
    y = x.right
    x.right = y.left  # Turn y's left subtree into x's right subtree
    
    if y.left:
        y.left.parent = x
        
    y.parent = x.parent 
    
    if x.parent is None:
        tree.root = y
    elif x == x.parent.left:
        x.parent.left = y
    else:
        x.parent.right = y
        
    y.left = x
    x.parent = y
```

## 13.2 Properties Check
Ideally, verification code runs `check_black_height(root)` to ensure validity.
