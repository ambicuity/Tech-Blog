---
layout: page
title: "215. Kth Largest Element in an Array"
permalink: /courses/leetcode/prob-215-kth-largest-element-in-an-array/
---

# 215. Kth Largest Element in an Array

## 1. The Question
Given an integer array `nums` and an integer `k`, return the `k`th largest element in the array.

Note that it is the `k`th largest element in the sorted order, not the `k`th distinct element.

Can you solve it without sorting?

### Example 1
**Input**: `nums = [3,2,1,5,6,4], k = 2`
**Output**: `5`

### Example 2
**Input**: `nums = [3,2,3,1,2,4,5,5,6], k = 4`
**Output**: `4`

---

## 2. Explanation
To find the `k`-th largest element:
1.  **Sorting**: $O(N \log N)$. Trivial.
2.  **Min-Heap**:
    -   Maintain a Min-Heap of size `k`.
    -   Iterate through `nums`.
    -   Add `num` to heap.
    -   If heap size > `k`, pop the smallest element (which is definitely not the k-th largest, it's smaller than at least k other elements seen so far).
    -   The root of the heap is the `k`-th largest.
    -   **Time**: $O(N \log k)$.
3.  **QuickSelect**: $O(N)$ average, $O(N^2)$ worst case.
    -   Partition array similar to QuickSort.
    -   If pivot index matches `target` (which is `len(nums) - k`), return pivot.
    -   Else recurse on appropriate half.

We will use **Min-Heap** as it's cleaner and $O(N \log k)$ is very efficient and consistent.

---

## 3. Pseudo Code
```text
heap = []
for x in nums:
    heappush(heap, x)
    if len(heap) > k:
        heappop(heap)
        
return heap[0]
```

---

## 4. Optimal Code (Python)

```python
import heapq

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        # Min heap of size k
        # The smallest element in a heap of size k (where we kept largest elements seen so far)
        # is the k-th largest element.
        heap = []
        for num in nums:
            heapq.heappush(heap, num)
            if len(heap) > k:
                heapq.heappop(heap)
                
        return heap[0]
```

---

## 5. Complexity
-   **Time**: $O(N \log k)$.
-   **Space**: $O(k)$.

## 6. Example Walkthrough
`[3,2,1,5,6,4]`, `k=2`.
1.  `3`. Heap `[3]`.
2.  `2`. Heap `[2, 3]`.
3.  `1`. Heap `[1, 3, 2]`. Pop `1`. `[2, 3]`.
4.  `5`. Heap `[2, 3, 5]`. Pop `2`. `[3, 5]`.
5.  `6`. Heap `[3, 5, 6]`. Pop `3`. `[5, 6]`.
6.  `4`. Heap `[4, 6, 5]`. Pop `4`. `[5, 6]`.
Top is `5`. Correct.
