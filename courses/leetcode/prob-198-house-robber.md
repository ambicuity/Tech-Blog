---
layout: page
title: "198. House Robber"
permalink: /courses/leetcode/prob-198-house-robber/
---

# 198. House Robber

## 1. The Question
You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed, the only constraint stopping you from robbing each of them is that adjacent houses have security systems connected and **it will automatically contact the police if two adjacent houses were broken into on the same night**.

Given an integer array `nums` representing the amount of money of each house, return the maximum amount of money you can rob tonight without alerting the police.

### Example 1
**Input**: `nums = [1,2,3,1]`
**Output**: `4`
**Explanation**: Rob 1 and 3. Total 4.

### Example 2
**Input**: `nums = [2,7,9,3,1]`
**Output**: `12`
**Explanation**: Rob 2, 9, 1. Total 12.

---

## 2. Explanation
DP State: `dp[i]` = Max money robbing first `i` houses.
Choices at house `i`:
1.  **Rob house `i`**: Must skip house `i-1`. Total = `nums[i] + dp[i-2]`.
2.  **Skip house `i`**: Total = `dp[i-1]`.

Recurrence: `dp[i] = max(dp[i-1], nums[i] + dp[i-2])`.

Space Optimization: Only need last two values.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
rob1, rob2 = 0, 0
for n in nums:
    temp = max(n + rob1, rob2)
    rob1 = rob2
    rob2 = temp
return rob2
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def rob(self, nums: list[int]) -> int:
        # rob1: max money excluding current house (i-2)
        # rob2: max money including possible current house (i-1)
        rob1, rob2 = 0, 0
        
        for n in nums:
            # option 1: rob this house (n) + best from 2 houses ago (rob1)
            # option 2: skip this house, keep best from 1 house ago (rob2)
            temp = max(n + rob1, rob2)
            rob1 = rob2
            rob2 = temp
            
        return rob2
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[2, 7, 9, 3, 1]`
1.  `n=2`. `temp = max(2+0, 0) = 2`. `r1=0, r2=2`.
2.  `n=7`. `temp = max(7+0, 2) = 7`. `r1=2, r2=7`.
3.  `n=9`. `temp = max(9+2, 7) = 11`. `r1=7, r2=11`.
4.  `n=3`. `temp = max(3+7, 11) = 11`. `r1=11, r2=11`.
5.  `n=1`. `temp = max(1+11, 11) = 12`. `r1=11, r2=12`.
Result 12.
