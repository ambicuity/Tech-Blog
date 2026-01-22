---
layout: page
title: "300. Longest Increasing Subsequence"
permalink: /courses/leetcode/prob-300-longest-increasing-subsequence/
---

# 300. Longest Increasing Subsequence

## 1. The Question
Given an integer array `nums`, return the length of the longest strictly increasing subsequence.

### Example 1
**Input**: `nums = [10,9,2,5,3,7,101,18]`
**Output**: `4`
**Explanation**: The longest increasing subsequence is `[2,3,7,101]`, therefore the length is 4.

---

## 2. Explanation
Method 1: Standard DP.
`dp[i]` = length of LIS ending at `i`.
`dp[i] = 1 + max(dp[j])` for all `j < i` where `nums[j] < nums[i]`.
Time: $O(N^2)$.

Method 2: Patience Sorting / tails array.
Maintain an array `tails` (or `sub`) where `sub[k]` stores the smallest tail of all increasing subsequences of length `k+1` found so far.
`sub` will be sorted.
For each x in nums:
-   If x > `sub[-1]`, append x.
-   Else, replace finding the first element in `sub` >= x (Binary Search) with x.

Time: $O(N \log N)$.

We will implement Method 2 as it's optimal.

---

## 3. Pseudo Code
```text
sub = []
for x in nums:
    if not sub or sub[-1] < x:
        sub.append(x)
    else:
        idx = bisect_left(sub, x)
        sub[idx] = x
return len(sub)
```

---

## 4. Optimal Code (Python)

```python
import bisect

class Solution:
    def lengthOfLIS(self, nums: list[int]) -> int:
        sub = []
        for x in nums:
            if not sub or sub[-1] < x:
                sub.append(x)
            else:
                # Find the first element in sub that is >= x
                idx = bisect.bisect_left(sub, x)
                sub[idx] = x
                
        return len(sub)
```

---

## 5. Complexity
-   **Time**: $O(N \log N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`[10,9,2,5,3,7,101,18]`
1.  `10`. `sub=[10]`.
2.  `9`. Replace 10. `sub=[9]`.
3.  `2`. Replace 9. `sub=[2]`.
4.  `5`. Append. `sub=[2, 5]`.
5.  `3`. Replace 5. `sub=[2, 3]`.
6.  `7`. Append. `sub=[2, 3, 7]`.
7.  `101`. Append. `sub=[2, 3, 7, 101]`.
8.  `18`. Replace 101. `sub=[2, 3, 7, 18]`.
Len 4.
Note: `sub` does not contain the actual LIS, but its length is correct.
