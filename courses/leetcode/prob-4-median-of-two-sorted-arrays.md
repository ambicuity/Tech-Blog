---
layout: page
title: "4. Median of Two Sorted Arrays"
permalink: /courses/leetcode/prob-4-median-of-two-sorted-arrays/
---

# 4. Median of Two Sorted Arrays

## 1. The Question
Given two sorted arrays `nums1` and `nums2` of size `m` and `n` respectively, return the median of the two sorted arrays.

The overall run time complexity should be `O(log (m+n))`.

### Example 1
**Input**: `nums1 = [1,3], nums2 = [2]`
**Output**: `2.00000`
**Explanation**: merged array = [1,2,3] and median is 2.

### Example 2
**Input**: `nums1 = [1,2], nums2 = [3,4]`
**Output**: `2.50000`
**Explanation**: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.

---

## 2. Explanation
We want to partition two arrays such that:
1.  Left side contains `(m + n + 1) // 2` elements.
2.  All elements in Left <= All elements in Right.
3.  Specifically: `nums1[i-1] <= nums2[j]` AND `nums2[j-1] <= nums1[i]`.
    -   Where `i` is partition index of `nums1`, `j` is partition index of `nums2`.
    -   `i + j = (m + n + 1) // 2`.

We binary search on `i` (smaller array).
-   If `nums1[i-1] > nums2[j]`: We took too many from `nums1`. Move left (`r = i - 1`).
-   If `nums2[j-1] > nums1[i]`: We took too few from `nums1` (or too many from `nums2`). Move right (`l = i + 1`).
-   Correct partition found:
    -   `maxLeft = max(nums1[i-1], nums2[j-1])`.
    -   `minRight = min(nums1[i], nums2[j])`.
    -   If odd total: `maxLeft`.
    -   If even total: `(maxLeft + minRight) / 2`.

-   **Time**: $O(\log(\min(M, N)))$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
if len(A) > len(B): swap(A, B)
m, n = len(A), len(B)
half = (m + n + 1) // 2
l, r = 0, m

while l <= r:
    i = (l + r) // 2
    j = half - i
    
    A_left = A[i-1] if i > 0 else -inf
    A_right = A[i] if i < m else inf
    B_left = B[j-1] if j > 0 else -inf
    B_right = B[j] if j < n else inf
    
    if A_left <= B_right and B_left <= A_right:
        if (m+n) % 2 == 1:
            return max(A_left, B_left)
        else:
            return (max(A_left, B_left) + min(A_right, B_right)) / 2
    elif A_left > B_right:
        r = i - 1
    else:
        l = i + 1
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        # Ensure nums1 is the smaller array to minimize search space
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1
            
        m, n = len(nums1), len(nums2)
        start, end = 0, m
        half_len = (m + n + 1) // 2
        
        while start <= end:
            partition_a = (start + end) // 2
            partition_b = half_len - partition_a
            
            # Edges
            max_left_a = float('-inf') if partition_a == 0 else nums1[partition_a - 1]
            min_right_a = float('inf') if partition_a == m else nums1[partition_a]
            
            max_left_b = float('-inf') if partition_b == 0 else nums2[partition_b - 1]
            min_right_b = float('inf') if partition_b == n else nums2[partition_b]
            
            # Check if valid partition
            if max_left_a <= min_right_b and max_left_b <= min_right_a:
                # Found correct partition
                if (m + n) % 2 == 1:
                    return max(max_left_a, max_left_b)
                else:
                    return (max(max_left_a, max_left_b) + min(min_right_a, min_right_b)) / 2.0
            
            # Adjust binary search range
            elif max_left_a > min_right_b:
                end = partition_a - 1
            else:
                start = partition_a + 1
                
        return 0.0
```

---

## 5. Complexity
-   **Time**: $O(\log(\min(M, N)))$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[1, 3]`, `[2]`. M=2, N=1. Swap -> `[2]`, `[1, 3]`. M=1, N=2.
Half = 2.
1.  `l=0, r=1`. `i=0`. `j=2`.
    -   `maxLeftA` = -inf, `minRightA` = 2.
    -   `maxLeftB` = 3, `minRightB` = inf.
    -   `inf <= inf` and `3 <= 2` -> False. `3 > 2`.
    -   `maxLeftB` > `minRightA`. `A_left` was too small. (Wait logic check)
    -   Logic: `maxLeftA <= minRightB` OK. `maxLeftB <= minRightA` FAIL (3 <= 2).
    -   Need larger `minRightA`, so larger `partition_a`. `l = i + 1`.
2.  `l=1, r=1`. `i=1`. `j=1`.
    -   `maxLeftA` = 2, `minRightA` = inf.
    -   `maxLeftB` = 1, `minRightB` = 3.
    -   `2 <= 3` OK. `1 <= inf` OK.
    -   Odd total. `max(2, 1) = 2`.
Result: 2.0.
