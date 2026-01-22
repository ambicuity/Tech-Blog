---
layout: page
title: "26. Remove Duplicates"
permalink: /courses/leetcode/prob-26-remove-duplicates/
---

# 26. Remove Duplicates from Sorted Array

## 1. The Question

Given an integer array `nums` sorted in **non-decreasing order**, remove the duplicates **in-place** such that each unique element appears only once. The relative order of the elements should be kept the same. Then return the number of unique elements `k`.

### Example 1
**Input**: `nums = [1,1,2]`
**Output**: `2, nums = [1,2,_]`

### Example 2
**Input**: `nums = [0,0,1,1,1,2,2,3,3,4]`
**Output**: `5, nums = [0,1,2,3,4,_,_,_,_,_]`

---

## 2. Explanation
The array is **sorted**. This is key. Duplicates are always grouped together.
We need to keep only one copy of each group.
Similar to "Remove Element", we use a `k` pointer (write index) and an `i` pointer (read index).
But here, the condition to keep `nums[i]` is: "Is it different from the previous element we wrote?"

---

## 3. Pseudo Code
```text
If array empty, return 0.
k = 1 (First element is always unique)
For i from 1 to length-1:
    If nums[i] != nums[i-1]: (Or check against nums[k-1])
        nums[k] = nums[i]
        k++
Return k
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def removeDuplicates(self, nums: list[int]) -> int:
        if not nums:
            return 0
            
        k = 1 # Write pointer
        
        for i in range(1, len(nums)):
            if nums[i] != nums[i-1]:
                nums[k] = nums[i]
                k += 1
                
        return k
```

---

## 5. Complexity
-   **Time**: $O(n)$. One pass.
-   **Space**: $O(1)$. In-place.

## 6. Example Walkthrough
`nums = [1, 1, 2]`

1.  `k=1`. Loop `i` from 1.
2.  `i=1`, `nums[1]=1`. `nums[1] == nums[0]`. Duplicate. Skip.
3.  `i=2`, `nums[2]=2`. `nums[2] != nums[1]`. Unique.
    `nums[k] = nums[i]` -> `nums[1] = 2`.
    `k` becomes 2.
End. Return 2. Array: `[1, 2, 2]`.
