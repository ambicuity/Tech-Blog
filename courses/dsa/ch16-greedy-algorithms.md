---
layout: page
title: "DSA Ch.16: Greedy Algorithms"
permalink: /courses/dsa/ch16-greedy-algorithms/
---

# Chapter 16: Greedy Algorithms

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 16

## 16.1 Activity Selection Problem
Maximum number of non-overlapping activities.
Strategy: Always pick the activity that **finishes earliest**.

```python
def activity_selection(activities):
    # Sort by finish time
    # Each activity is (start, finish)
    activities.sort(key=lambda x: x[1])
    
    selected = [activities[0]]
    last_finish_time = activities[0][1]
    
    for i in range(1, len(activities)):
        if activities[i][0] >= last_finish_time:
            selected.append(activities[i])
            last_finish_time = activities[i][1]
            
    return selected

acts = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11)]
print(activity_selection(acts))
# Output: [(1, 4), (5, 7), (8, 11)]
```

## 16.2 Huffman Coding
Greedily build tree by combining two lowest frequency nodes.

```python
import heapq

def huffman_coding(freqs):
    heap = [[weight, [symbol, ""]] for symbol, weight in freqs.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
            
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        
    return heap[0][1:]

print(huffman_coding({'a': 45, 'b': 13, 'c': 12, 'd': 16, 'e': 9, 'f': 5}))
```
