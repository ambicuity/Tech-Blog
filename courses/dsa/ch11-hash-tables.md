---
layout: page
title: "DSA Ch.11: Hash Tables"
permalink: /courses/dsa/ch11-hash-tables/
---

# Chapter 11: Hash Tables

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 11

## 11.1 Implementation (Chaining)

```python
class HashTable:
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(size)]
        
    def _hash(self, key):
        return hash(key) % self.size
        
    def insert(self, key, value):
        idx = self._hash(key)
        # Check update
        for pair in self.table[idx]:
            if pair[0] == key:
                pair[1] = value
                return
        self.table[idx].append([key, value])
        
    def get(self, key):
        idx = self._hash(key)
        for pair in self.table[idx]:
            if pair[0] == key:
                return pair[1]
        return None
        
    def delete(self, key):
        idx = self._hash(key)
        for i, pair in enumerate(self.table[idx]):
            if pair[0] == key:
                del self.table[idx][i]
                return True
        return False
```

## 11.2 Performance
-   Expected time for all operations is $O(1 + \alpha)$, where $\alpha = N/M$.
-   Worst case $O(N)$ (all hash to same bucket).
