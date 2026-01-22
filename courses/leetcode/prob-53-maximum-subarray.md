---
layout: page
title: "53. Maximum Subarray"
permalink: /courses/leetcode/prob-53-maximum-subarray/
---

# 53. Maximum Subarray

## 1. The Question
Given an integer array `nums`, find the subarray with the largest sum, and return its sum.

### Example 1
**Input**: `nums = [-2,1,-3,4,-1,2,1,-5,4]`
**Output**: `6`
**Explanation**: The subarray `[4,-1,2,1]` has the largest sum `6`.

### Example 2
**Input**: `nums = [1]`
**Output**: `1`

---

## 2. Explanation
This is the classic **Kadane's Algorithm** problem.
We iterate through the array, maintaining a `current_sum`.
At each step, we have two choices:
1.  Add the current element to the existing subarray.
2.  Start a new subarray with the current element (if the previous sum was negative, it drags us down).

Formula: `current_sum = max(num, current_sum + num)`
`max_sum = max(max_sum, current_sum)`

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
max_so_far = nums[0]
curr_max = nums[0]

for x in nums[1:]:
    curr_max = max(x, curr_max + x)
    max_so_far = max(max_so_far, curr_max)

return max_so_far
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        if not nums:
            return 0
            
        max_so_far = nums[0]
        curr_max = nums[0]
        
        for i in range(1, len(nums)):
            # Either extend the previous subarray or start a new one
            curr_max = max(nums[i], curr_max + nums[i])
            max_so_far = max(max_so_far, curr_max)
            
        return max_so_far
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[-2, 1, -3, 4, -1, 2, 1, -5, 4]`

1.  Init: `max=-2`, `curr=-2`.
2.  `1`: `curr = max(1, -2+1) = 1`. `max=1`.
3.  `-3`: `curr = max(-3, 1-3) = -2`. `max=1`.
4.  `4`: `curr = max(4, -2+4) = 4`. `max=4`.
5.  `-1`: `curr = max(-1, 3) = 3`. `max=4`.
6.  `2`: `curr = max(2, 5) = 5`. `max=5`.
7.  `1`: `curr = max(1, 6) = 6`. `max=6`.
8.  `-5`: `curr = max(-5, 1) = 1`. `max=6`.
9.  `4`: `curr = max(4, 5) = 5`. `max=6`.
Result: 6.
