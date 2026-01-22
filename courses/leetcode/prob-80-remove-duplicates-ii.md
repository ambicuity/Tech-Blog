---
layout: page
title: "80. Remove Duplicates II"
permalink: /courses/leetcode/prob-80-remove-duplicates-ii/
---

# 80. Remove Duplicates from Sorted Array II

## 1. The Question
Given a sorted integer array `nums`, remove the duplicates in-place such that each unique element appears **at most twice**. The relative order of the elements should be kept the same.

### Example 1
**Input**: `nums = [1,1,1,2,2,3]`
**Output**: `5, nums = [1,1,2,2,3,_]`
**Explanation**: '1' appears too many times (3). We keep two.

---

## 2. Explanation
Same as Problem 26 (Remove Duplicates), but our "check" condition is looser.
We can write a number `x` if:
1.  We haven't written two of them yet.
Since array is sorted, we just check against `nums[k-2]`. If `nums[i] == nums[k-2]`, it means we already have two copies (at k-2 and k-1). So we skip.

---

## 3. Pseudo Code
```text
If len < 3, return len.
k = 2
For i from 2 to length-1:
    If nums[i] != nums[k-2]:
        nums[k] = nums[i]
        k++
Return k
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def removeDuplicates(self, nums: list[int]) -> int:
        if len(nums) <= 2:
            return len(nums)
            
        k = 2  # The first two elements are always allowed
        
        for i in range(2, len(nums)):
            # If current element is different from the one two steps back,
            # it means we haven't exhausted the "allowance" of 2.
            if nums[i] != nums[k - 2]:
                nums[k] = nums[i]
                k += 1
                
        return k
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`nums = [1, 1, 1, 2]`

1.  `k=2`. Start `i=2`.
2.  `i=2`. `val=1`. `nums[k-2]` -> `nums[0]` is 1. `1 == 1`. Skip.
3.  `i=3`. `val=2`. `nums[k-2]` -> `nums[0]` is 1. `2 != 1`. Write.
    `nums[k] = 2` -> `nums[2] = 2`. `k=3`.
Return 3.
