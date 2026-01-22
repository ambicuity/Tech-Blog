---
layout: page
title: "27. Remove Element"
permalink: /courses/leetcode/prob-27-remove-element/
---

# 27. Remove Element

## 1. The Question

Given an integer array `nums` and an integer `val`, remove all occurrences of `val` in `nums` **in-place**. The order of the elements may be changed. Then return the number of elements in `nums` which are not equal to `val`.
Consider the number of elements in `nums` which are not equal to `val` be `k`, to get accepted, you need to do the following things:
- Change the array `nums` such that the first `k` elements of `nums` contain the elements which are not equal to `val`.
- Return `k`.

### Example 1
**Input**: `nums = [3,2,2,3], val = 3`
**Output**: `2, nums = [2,2,_,_]`

### Example 2
**Input**: `nums = [0,1,2,2,3,0,4,2], val = 2`
**Output**: `5, nums = [0,1,4,0,3,_,_,_]`

---

## 2. Explanation for Understanding
We need to "delete" elements equal to `val`. Since arrays are fixed size in memory blocks (conceptually), we can't literally delete. We just need to move the "good" elements to the front and return the count.
The elements after index `k` don't matter (garbage).

### Approach (Two Pointers)
One pointer `k` keeps track of the position where the next "good" element should go.
One pointer `i` iterates through the whole array.
If `nums[i]` is a good element (not `val`), put it at `nums[k]` and increment `k`.

---

## 3. Pseudo Code

```text
k = 0
For i from 0 to length(nums)-1:
    If nums[i] != val:
        nums[k] = nums[i]
        k++
Return k
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def removeElement(self, nums: list[int], val: int) -> int:
        k = 0
        for i in range(len(nums)):
            if nums[i] != val:
                nums[k] = nums[i]
                k += 1
        return k
```

---

## 5. Complexity Analysis
-   **Time Complexity**: $O(n)$. We pass through the array once.
-   **Space Complexity**: $O(1)$. In-place modification.

---

## 6. Example Walkthrough
`nums = [3, 2, 2, 3]`, `val = 3`

1.  `i=0`, `nums[0]=3`. Equal to val. Skip. (k=0)
2.  `i=1`, `nums[1]=2`. Not equal.
    `nums[k] = nums[i]` -> `nums[0] = 2`.
    `k` becomes 1.
3.  `i=2`, `nums[2]=2`. Not equal.
    `nums[k] = nums[i]` -> `nums[1] = 2`.
    `k` becomes 2.
4.  `i=3`, `nums[3]=3`. Equal. Skip.

Final `k=2`. Array looks like `[2, 2, 2, 3]`. First 2 elements are valid.
