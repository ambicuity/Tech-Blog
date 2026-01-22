---
layout: page
title: "153. Find Minimum in Rotated Sorted Array"
permalink: /courses/leetcode/prob-153-find-minimum-in-rotated-sorted-array/
---

# 153. Find Minimum in Rotated Sorted Array

## 1. The Question
Suppose an array of length `n` sorted in ascending order is rotated between `1` and `n` times. Given the sorted rotated array `nums` of **unique** elements, return the minimum element of this array.

You must write an algorithm that runs in `O(log n)` time.

### Example 1
**Input**: `nums = [3,4,5,1,2]`
**Output**: `1`
**Explanation**: Original `[1,2,3,4,5]` rotated 3 times.

### Example 2
**Input**: `nums = [11,13,15,17]`
**Output**: `11`
**Explanation**: Rotated 4 times (same).

---

## 2. Explanation
We want to find the "pivot" point where the rotation happens.
Compare `nums[mid]` with `nums[right]`.
-   If `nums[mid] > nums[right]`:
    -   The minimum must be to the **right** of `mid`. (e.g. `[3,4,5,1,2]`, mid=5, right=2. Min is in `[1,2]`).
    -   `left = mid + 1`.
-   If `nums[mid] < nums[right]`:
    -   The minimum could be `mid` or to the **left**. (e.g. `[5,1,2,3,4]`, mid=2, right=4. Min is 1).
    -   `right = mid`.
-   `nums[mid] == nums[right]` impossible as elements are unique.

Stop when `left == right`.

-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
l, r = 0, n-1
while l < r:
    mid = (l+r)//2
    if nums[mid] > nums[r]:
        l = mid + 1
    else:
        r = mid
return nums[l]
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def findMin(self, nums: list[int]) -> int:
        left, right = 0, len(nums) - 1
        
        while left < right:
            mid = (left + right) // 2
            
            # If mid element is greater than rightmost element,
            # min value must be to the right of mid.
            if nums[mid] > nums[right]:
                left = mid + 1
            # Otherwise, min is at mid or to the left.
            else:
                right = mid
                
        return nums[left]
```

---

## 5. Complexity
-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[3,4,5,1,2]`
1.  `l=0, r=4`. `Mid=2`. `Val=5`.
2.  `5 > 2`. `l = 3`.
3.  `l=3, r=4`. `Mid=3`. `Val=1`.
4.  `1 < 2`. `r = 3`.
5.  `l=3, r=3`. Return `nums[3] = 1`.
Correct.
