---
layout: page
title: "DSA Ch.7: Quicksort"
permalink: /courses/dsa/ch7-quicksort/
---

# Chapter 7: Quicksort

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 7

## 7.1 Python Implementation
Standard in-place Quicksort with Lomuto partition.

```python
import random

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def randomized_partition(arr, low, high):
    rand_idx = random.randint(low, high)
    arr[rand_idx], arr[high] = arr[high], arr[rand_idx]
    return partition(arr, low, high)

def quicksort(arr, low, high):
    if low < high:
        pi = randomized_partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)

# Usage
data = [10, 7, 8, 9, 1, 5]
quicksort(data, 0, len(data) - 1)
print(data) # [1, 5, 7, 8, 9, 10]
```

## 7.2 Analysis
-   **Worst Case**: $O(n^2)$ (Sorted array, if not randomized).
-   **Expected**: $O(n \lg n)$.
-   **Space**: $O(\lg n)$ stack depth.
