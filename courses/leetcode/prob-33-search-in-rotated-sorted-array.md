---
layout: page
title: "33. Search in Rotated Sorted Array"
permalink: /courses/leetcode/prob-33-search-in-rotated-sorted-array/
---

# 33. Search in Rotated Sorted Array

## 1. The Question
There is an integer array `nums` sorted in ascending order (with distinct values).
Prior to being passed to your function, `nums` is **possibly rotated** at an unknown pivot index `k` ( `1 <= k < nums.length`) such that the resulting array is `[nums[k], nums[k+1], ..., nums[n-1], nums[0], nums[1], ..., nums[k-1]]`.

Given the array `nums` after the possible rotation and an integer `target`, return the index of `target` if it is in `nums`, or `-1` if it is not in `nums`.

You must write an algorithm with `O(log n)` runtime complexity.

### Example 1
**Input**: `nums = [4,5,6,7,0,1,2], target = 0`
**Output**: `4`

### Example 2
**Input**: `nums = [4,5,6,7,0,1,2], target = 3`
**Output**: `-1`

---

## 2. Explanation
In a rotated sorted array, one half is always **normally sorted**.
`[4,5,6,7,0,1,2]`. Mid `7`.
-   Left side `[4,5,6]` is sorted.
-   Right side `[0,1,2]` is sorted.
If `nums[l] <= nums[mid]`, left side is sorted.
We check if `target` is in the range `[nums[l], nums[mid]]`.
-   If yes, search left.
-   Else, search right.

If `nums[l] > nums[mid]`, Right side must be sorted.
We check if `target` is in the range `[nums[mid], nums[r]]`.
-   If yes, search right.
-   Else, search left.

-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
l, r = 0, n-1
while l <= r:
    mid = (l+r)//2
    if target == nums[mid]: return mid
    
    # Left Sorted
    if nums[l] <= nums[mid]:
        if nums[l] <= target < nums[mid]:
            r = mid - 1
        else:
            l = mid + 1
    # Right Sorted
    else:
        if nums[mid] < target <= nums[r]:
            l = mid + 1
        else:
            r = mid - 1
return -1
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def search(self, nums: list[int], target: int) -> int:
        left, right = 0, len(nums) - 1
        
        while left <= right:
            mid = (left + right) // 2
            
            if nums[mid] == target:
                return mid
                
            # Check if left half is sorted
            if nums[left] <= nums[mid]:
                if nums[left] <= target < nums[mid]:
                    right = mid - 1
                else:
                    left = mid + 1
            # Otherwise, right half must be sorted
            else:
                if nums[mid] < target <= nums[right]:
                    left = mid + 1
                else:
                    right = mid - 1
                    
        return -1
```

---

## 5. Complexity
-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[4,5,6,7,0,1,2]`, `target=0`
1.  `l=0, r=6`. `Mid=3`. Val `7`.
2.  Left Sorted (`4 <= 7`).
3.  Is `0` in `[4, 7]`? No.
4.  Search Right. `l = 4`.
5.  `l=4, r=6`. `Mid=5`. Val `1`.
6.  Left Sorted (`0 <= 1`).
7.  Is `0` in `[0, 1]`? Yes.
8.  Search Left. `r = 4`.
9.  `l=4, r=4`. `Mid=4`. Val `0`. Found.
