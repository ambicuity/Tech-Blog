---
layout: page
title: "DSA Ch.8: Linear Sort"
permalink: /courses/dsa/ch8-linear-sort/
---

# Chapter 8: Sorting in Linear Time

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 8

## 8.1 Counting Sort
Efficient when range of input $k$ is not much larger than $n$.

```python
def counting_sort(arr):
    if not arr: return []
    
    # 1. Find range
    max_val = max(arr)
    min_val = min(arr) # Handle negatives by shifting
    range_of_elements = max_val - min_val + 1
    
    # 2. Initialize count array
    count = [0] * range_of_elements
    output = [0] * len(arr)
    
    # 3. Store counts
    for num in arr:
        count[num - min_val] += 1
        
    # 4. Cumulative counts (positions)
    for i in range(1, len(count)):
        count[i] += count[i - 1]
        
    # 5. Build output array (Reverse order for stability)
    for i in range(len(arr) - 1, -1, -1):
        num = arr[i]
        pos = count[num - min_val] - 1
        output[pos] = num
        count[num - min_val] -= 1
        
    return output

# Usage
data = [4, 2, 2, 8, 3, 3, 1]
print(counting_sort(data)) # [1, 2, 2, 3, 3, 4, 8]
```

## 8.2 Radix Sort
Sorts column by column.
Complexity: $O(d(n+k))$.
