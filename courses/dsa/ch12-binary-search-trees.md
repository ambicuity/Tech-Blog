---
layout: page
title: "DSA Ch.12: BST"
permalink: /courses/dsa/ch12-binary-search-trees/
---

# Chapter 12: Binary Search Trees (BST)

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 12

## 12.1 Python Implementation

```python
class TreeNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

def insert(root, key):
    if root is None:
        return TreeNode(key)
    if key < root.key:
        root.left = insert(root.left, key)
    else:
        root.right = insert(root.right, key)
    return root

def search(root, key):
    if root is None or root.key == key:
        return root
    if key < root.key:
        return search(root.left, key)
    return search(root.right, key)

def inorder_traversal(root):
    res = []
    if root:
        res = inorder_traversal(root.left)
        res.append(root.key)
        res = res + inorder_traversal(root.right)
    return res

def min_value_node(node):
    current = node
    while current.left:
        current = current.left
    return current

def delete_node(root, key):
    if not root: return root
    
    if key < root.key:
        root.left = delete_node(root.left, key)
    elif key > root.key:
        root.right = delete_node(root.right, key)
    else:
        # Case 1 & 2: One child or no child
        if not root.left: return root.right
        if not root.right: return root.left
        
        # Case 3: Two children
        # Get inorder successor (smallest in right subtree)
        temp = min_value_node(root.right)
        root.key = temp.key
        root.right = delete_node(root.right, temp.key)
        
    return root
```
