---
layout: page
title: "DSA Ch.10: Elementary DS"
permalink: /courses/dsa/ch10-elementary-data-structures/
---

# Chapter 10: Elementary Data Structures

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 10

## 10.1 Stack (LIFO)
```python
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None
    
    def is_empty(self):
        return len(self.items) == 0
```

## 10.2 Linked List
```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        
    def insert(self, data):
        # Insert at front O(1)
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        
    def search(self, key):
        current = self.head
        while current:
            if current.data == key:
                return current
            current = current.next
        return None
        
    def delete(self, key):
        current = self.head
        prev = None
        while current and current.data != key:
            prev = current
            current = current.next
            
        if current: # Found
            if prev:
                prev.next = current.next
            else:
                self.head = current.next # Deleting head
```
