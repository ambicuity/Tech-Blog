---
layout: page
title: "88. Merge Sorted Array"
permalink: /courses/leetcode/prob-88-merge-sorted-array/
---

# 88. Merge Sorted Array

## 1. The Question

You are given two integer arrays `nums1` and `nums2`, sorted in **non-decreasing order**, and two integers `m` and `n`, representing the number of elements in `nums1` and `nums2` respectively.

**Merge** `nums1` and `nums2` into a single array sorted in **non-decreasing order**.

The final sorted array should not be returned by the function, but instead be stored inside the array `nums1`. To accommodate this, `nums1` has a length of `m + n`, where the first `m` elements denote the elements that should be merged, and the last `n` elements are set to `0` and should be ignored. `nums2` has a length of `n`.

### Example 1
**Input**: `nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3`
**Output**: `[1,2,2,3,5,6]`
**Explanation**: The arrays we are merging are `[1,2,3]` and `[2,5,6]`. The result is `[1,2,2,3,5,6]`.

### Example 2
**Input**: `nums1 = [1], m = 1, nums2 = [], n = 0`
**Output**: `[1]`

---

## 2. Explanation for Understanding

We have two sorted arrays. We need to merge them into the first one.
`nums1` has enough extra space at the end to hold `nums2`.

### Naive Approach
Merge `nums2` into `nums1` starting at index `m`, then run a Sort algorithm.
-   Cost: `(m+n) log(m+n)`.
-   Not optimal because it ignores the fact that arrays are *already* sorted.

### Optimal Approach (Two Pointers)
We can use two pointers to iterate through both arrays from the beginning. However, since we need to write into `nums1`, writing to the beginning would overwrite elements we haven't processed yet (requiring shifting $O(N)$).
**Trick**: Start from the **End**.
Fill `nums1` from the back (index `m+n-1`) to the front. The largest element between `nums1` and `nums2` goes to the last available position.

---

## 3. Pseudo Code

```text
p1 = m - 1 (Pointer for end of valid nums1)
p2 = n - 1 (Pointer for end of nums2)
p = m + n - 1 (Pointer for end of total nums1)

While p2 >= 0:
    If p1 >= 0 AND nums1[p1] > nums2[p2]:
        nums1[p] = nums1[p1]
        p1--
    Else:
        nums1[p] = nums2[p2]
        p2--
    p--
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def merge(self, nums1: list[int], m: int, nums2: list[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.
        """
        p1 = m - 1
        p2 = n - 1
        p = m + n - 1
        
        while p2 >= 0:
            if p1 >= 0 and nums1[p1] > nums2[p2]:
                nums1[p] = nums1[p1]
                p1 -= 1
            else:
                nums1[p] = nums2[p2]
                p2 -= 1
            p -= 1
```

---

## 5. Complexity Analysis

-   **Time Complexity**: $O(m + n)$. We iterate through each element of both arrays exactly once.
-   **Space Complexity**: $O(1)$. We are doing the merge in-place without using extra data structures.

---

## 6. Example Walkthrough

`nums1 = [1, 2, 3, 0, 0, 0]`, `m=3`
`nums2 = [2, 5, 6]`, `n=3`

1.  `p1=2` (val 3), `p2=2` (val 6). Compare 3 and 6. 6 is larger.
    `nums1[5] = 6`. `p2` becomes 1.
2.  `nums1 = [1, 2, 3, 0, 0, 6]`
    `p1=2` (3), `p2=1` (5). 5 is larger.
    `nums1[4] = 5`. `p2` becomes 0.
3.  `nums1 = [1, 2, 3, 0, 5, 6]`
    `p1=2` (3), `p2=0` (2). 3 is larger.
    `nums1[3] = 3`. `p1` becomes 1.
4.  `nums1 = [1, 2, 3, 3, 5, 6]`
    ... and so on.
