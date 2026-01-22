---
layout: page
title: "918. Maximum Sum Circular Subarray"
permalink: /courses/leetcode/prob-918-maximum-sum-circular-subarray/
---

# 918. Maximum Sum Circular Subarray

## 1. The Question
Given a **circular integer array** `nums` of length `n`, return the maximum possible sum of a non-empty subarray of `nums`.

A **circular array** means the end of the array connects to the beginning of the array. Formally, the next element of `nums[i]` is `nums[(i + 1) % n]` and the previous element of `nums[i]` is `nums[(i - 1 + n) % n]`.

### Example 1
**Input**: `nums = [1,-2,3,-2]`
**Output**: `3`
**Explanation**: Subarray `[3]` has max sum 3.

### Example 2
**Input**: `nums = [5,-3,5]`
**Output**: `10`
**Explanation**: Subarray `[5,5]` has max sum 5 + 5 = 10.

---

## 2. Explanation
A circular subarray can be:
1.  **Normal**: No wrapping. (Standard Kadane's Max).
2.  **Wrapped**: Uses end and start. This means it excludes a middle subarray.
    -   `Total Sum - Min Subarray Sum`.

So, `Result = max(KadaneMax, Total - KadaneMin)`.

**Edge Case**: If all numbers are negative.
-   `KadaneMax` will be the max single element (e.g. -1).
-   `Total - KadaneMin`: `KadaneMin` will be `Total` (sum of all). So result is `0`.
-   Taking `0` implies empty array, but we need non-empty.
-   If `KadaneMax < 0`, return `KadaneMax` immediately.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
max_sum = min_sum = total = 0
curr_max = curr_min = 0

for x in nums:
    curr_max = max(x, curr_max + x)
    max_sum = max(max_sum, curr_max)
    
    curr_min = min(x, curr_min + x)
    min_sum = min(min_sum, curr_min)
    
    total += x

if max_sum > 0:
    return max(max_sum, total - min_sum)
else:
    return max_sum
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def maxSubarraySumCircular(self, nums: list[int]) -> int:
        if not nums:
            return 0
            
        # Initialize
        # Using first element for proper tracking of all-negatives case
        curr_max = nums[0]
        max_sum = nums[0]
        
        curr_min = nums[0]
        min_sum = nums[0]
        
        total = nums[0]
        
        for i in range(1, len(nums)):
            x = nums[i]
            
            # Kadane's Max
            curr_max = max(x, curr_max + x)
            max_sum = max(max_sum, curr_max)
            
            # Kadane's Min
            curr_min = min(x, curr_min + x)
            min_sum = min(min_sum, curr_min)
            
            total += x
            
        # If all numbers are negative, max_sum corresponds to the maximum single element.
        # In this case circular sum (total - min_sum) would be 0 (empty sub), which is invalid.
        if max_sum < 0:
            return max_sum
            
        return max(max_sum, total - min_sum)
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[5, -3, 5]`
1.  Init: `max=5`, `currM=5`, `min=5`, `currm=5`, `tot=5`.
2.  `-3`:
    -   `currM=max(-3, 2)=2`. `max=5`.
    -   `currm=min(-3, 2)=-3`. `min=-3`.
    -   `tot=2`.
3.  `5`:
    -   `currM=max(5, 7)=7`. `max=7`.
    -   `currm=min(5, 2)=2`. `min=-3`.
    -   `tot=7`.

Result: `max(7, 7 - (-3) = 10) = 10`. Correct.
