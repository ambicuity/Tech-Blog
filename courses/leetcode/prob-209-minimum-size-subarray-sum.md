---
layout: page
title: "209. Minimum Size Subarray Sum"
permalink: /courses/leetcode/prob-209-minimum-size-subarray-sum/
---

# 209. Minimum Size Subarray Sum

## 1. The Question
Given an array of positive integers `nums` and a positive integer `target`, return the minimal length of a **subarray** whose sum is greater than or equal to `target`. If there is no such subarray, return `0` instead.

### Example 1
**Input**: `target = 7, nums = [2,3,1,2,4,3]`
**Output**: `2`
**Explanation**: The subarray `[4,3]` has the minimal length under the problem constraint.

### Example 2
**Input**: `target = 4, nums = [1,4,4]`
**Output**: `1`

### Example 3
**Input**: `target = 11, nums = [1,1,1,1,1,1,1,1]`
**Output**: `0`

---

## 2. Explanation
We need a contiguous subarray with `sum >= target`.
Since all numbers are positive, the sum increases as we add elements and decreases as we remove elements. This monotonicity allows us to use a **Sliding Window**.

### Approach: Sliding Window
1.  Initialize `left = 0`, `current_sum = 0`, `min_props = infinity`.
2.  Iterate `right` from `0` to `n`.
3.  Add `nums[right]` to `current_sum`.
4.  **While** `current_sum >= target`:
    -   Update `min_props` with `right - left + 1`.
    -   Subtract `nums[left]` from `current_sum`.
    -   Increment `left` (shrink the window).

-   **Time**: $O(n)$. Each element is added once and removed at most once.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
n = len(nums)
left = 0
current_sum = 0
min_len = infinity

For right from 0 to n-1:
    current_sum += nums[right]
    
    While current_sum >= target:
        min_len = min(min_len, right - left + 1)
        current_sum -= nums[left]
        left++

Return min_len if found else 0
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def minSubArrayLen(self, target: int, nums: list[int]) -> int:
        n = len(nums)
        left = 0
        current_sum = 0
        min_len = float('inf')
        
        for right in range(n):
            current_sum += nums[right]
            
            # While the window is valid, try to shrink it
            while current_sum >= target:
                min_len = min(min_len, right - left + 1)
                
                # Shrink window from the left
                current_sum -= nums[left]
                left += 1
                
        return min_len if min_len != float('inf') else 0
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`target = 7`, `nums = [2, 3, 1, 2, 4, 3]`

1.  `R=0 (2)`. Sum=2.
2.  `R=1 (3)`. Sum=5.
3.  `R=2 (1)`. Sum=6.
4.  `R=3 (2)`. Sum=8.
    -   `8 >= 7`. `Len = 4`. `[2,3,1,2]`.
    -   Shrink L (2). Sum=6. `L=1`.
5.  `R=4 (4)`. Sum=10.
    -   `10 >= 7`. `Len=4`. `[3,1,2,4]`.
    -   Shrink L (3). Sum=7. `L=2`.
    -   `7 >= 7`. `Len = 3`. `[1,2,4]`.
    -   Shrink L (1). Sum=6. `L=3`.
6.  `R=5 (3)`. Sum=9.
    -   `9 >= 7`. `Len=3`. `[2,4,3]`.
    -   Shrink L (2). Sum=7. `L=4`.
    -   `7 >= 7`. `Len = 2`. `[4,3]`. (New Min!)
    -   Shrink L (4). Sum=3. `L=5`.

Result: 2.
