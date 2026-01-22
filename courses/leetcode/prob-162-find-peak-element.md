---
layout: page
title: "162. Find Peak Element"
permalink: /courses/leetcode/prob-162-find-peak-element/
---

# 162. Find Peak Element

## 1. The Question
A peak element is an element that is strictly greater than its neighbors.
Given a **0-indexed** integer array `nums`, find a peak element, and return its index. If the array contains multiple peaks, return the index to **any of the peaks**.

You may imagine that `nums[-1] = nums[n] = -∞`. In other words, an element is always considered to be strictly greater than a neighbor that is outside the array.

You must write an algorithm that runs in `O(log n)` time.

### Example 1
**Input**: `nums = [1,2,3,1]`
**Output**: `2`
**Explanation**: 3 is a peak element and your function should return the index number 2.

### Example 2
**Input**: `nums = [1,2,1,3,5,6,4]`
**Output**: `5`
**Explanation**: Your function can return either index number 1 where the peak element is 2, or index number 5 where the peak element is 6.

---

## 2. Explanation
To do this in $O(\log n)$, we use Binary Search.
If we look at `nums[mid]` and compares it to `nums[mid+1]`:
-   If `nums[mid] < nums[mid+1]`, it means we are on a "uphill" slope. A peak MUST exist to the **right** (eventually it goes down to $-\infty$).
-   If `nums[mid] > nums[mid+1]`, we are on a "downhill" slope. A peak MUST exist to the **left** (or at `mid`).

We narrow the search space until `l == r`.

-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
l, r = 0, n-1
while l < r:
    mid = (l + r) // 2
    if nums[mid] < nums[mid+1]:
        # Uphill, peak is to the right
        l = mid + 1
    else:
        # Downhill (or peak), looking left is safer.
        # Actually since nums[mid] > nums[mid+1], mid COULD be the peak.
        r = mid
return l
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def findPeakElement(self, nums: list[int]) -> int:
        left, right = 0, len(nums) - 1
        
        while left < right:
            mid = (left + right) // 2
            
            if nums[mid] < nums[mid+1]:
                # We are in an ascending slope. Peak must be to the right.
                left = mid + 1
            else:
                # We are in a descending slope (or local max). Peak is at mid or to the left.
                right = mid
                
        return left
```

---

## 5. Complexity
-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[1, 2, 3, 1]`
1.  `l=0, r=3`. `Mid=1`. `Val=2`.
2.  `nums[1](2) < nums[2](3)`. Increasing. `l = 2`.
3.  `l=2, r=3`. `Mid=2`. `Val=3`.
4.  `nums[2](3) > nums[3](1)`. Decreasing. `r=2`.
5.  `l=2, r=2`. Loop ends. Return 2.
Correct.
