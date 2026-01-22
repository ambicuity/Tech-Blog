---
layout: page
title: "DSA Ch.6: Heapsort"
permalink: /courses/dsa/ch6-heapsort/
---

# Chapter 6: Heapsort

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 6

## 6.1 Python Implementation
A Heap class implementing Max-Heap logic.

```python
class MaxHeap:
    def __init__(self, arr=[]):
        self.heap = arr
        self.build_max_heap()
    
    def parent(self, i):
        return (i - 1) // 2
    
    def left(self, i):
        return 2 * i + 1
    
    def right(self, i):
        return 2 * i + 2
    
    def max_heapify(self, i, n):
        l = self.left(i)
        r = self.right(i)
        largest = i
        
        if l < n and self.heap[l] > self.heap[largest]:
            largest = l
        if r < n and self.heap[r] > self.heap[largest]:
            largest = r
            
        if largest != i:
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            self.max_heapify(largest, n)
            
    def build_max_heap(self):
        n = len(self.heap)
        # Start from last non-leaf node and go up
        for i in range(n // 2 - 1, -1, -1):
            self.max_heapify(i, n)
            
    def sort(self):
        self.build_max_heap()
        n = len(self.heap)
        for i in range(n - 1, 0, -1):
            # Swap root (max) with end
            self.heap[0], self.heap[i] = self.heap[i], self.heap[0]
            # Restore property for reduced heap
            self.max_heapify(0, i)
        return self.heap

# Usage
arr = [12, 11, 13, 5, 6, 7]
h = MaxHeap(arr)
sorted_arr = h.sort()
print(sorted_arr) # [5, 6, 7, 11, 12, 13]
```

## 6.2 Complexity
-   `Max-Heapify`: $O(\lg n)$
-   `Build-Max-Heap`: $O(n)$
-   `Heapsort`: $O(n \lg n)$
