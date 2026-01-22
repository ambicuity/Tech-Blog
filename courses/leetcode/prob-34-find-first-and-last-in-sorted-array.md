---
layout: page
title: "34. Find First and Last Position of Element in Sorted Array"
permalink: /courses/leetcode/prob-34-find-first-and-last-in-sorted-array/
---

# 34. Find First and Last Position of Element in Sorted Array

## 1. The Question
Given an array of integers `nums` sorted in non-decreasing order, find the starting and ending position of a given `target` value.

If `target` is not found in the array, return `[-1, -1]`.

You must write an algorithm with `O(log n)` runtime complexity.

### Example 1
**Input**: `nums = [5,7,7,8,8,10], target = 8`
**Output**: `[3,4]`

### Example 2
**Input**: `nums = [5,7,7,8,8,10], target = 6`
**Output**: `[-1,-1]`

---

## 2. Explanation
We need two binary searches:
1.  Find the **first** occurrence (Left Bound).
    -   If `nums[mid] == target`, record possible answer, search left (`r = mid - 1`).
2.  Find the **last** occurrence (Right Bound).
    -   If `nums[mid] == target`, record possible answer, search right (`l = mid + 1`).

-   **Time**: $2 \cdot O(\log N) = O(\log N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
def searchRange(nums, target):
    def findBound(isFirst):
        l, r = 0, len(nums)-1
        ans = -1
        while l <= r:
            mid = (l+r)//2
            if nums[mid] == target:
                ans = mid
                if isFirst: r = mid - 1
                else: l = mid + 1
            elif nums[mid] < target:
                l = mid + 1
            else:
                r = mid - 1
        return ans

    start = findBound(True)
    if start == -1: return [-1, -1]
    end = findBound(False)
    return [start, end]
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def searchRange(self, nums: list[int], target: int) -> list[int]:
        
        def findBound(isFirst):
            left, right = 0, len(nums) - 1
            ans = -1
            
            while left <= right:
                mid = (left + right) // 2
                
                if nums[mid] == target:
                    ans = mid
                    if isFirst:
                        right = mid - 1  # Look for earlier occurrences
                    else:
                        left = mid + 1   # Look for later occurrences
                elif nums[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1
            return ans
            
        start = findBound(True)
        if start == -1:
            return [-1, -1]
            
        end = findBound(False)
        return [start, end]
```

---

## 5. Complexity
-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[5, 7, 7, 8, 8, 10]`, `8`.
1.  Find First:
    -   Mid `8` (idx 3). Ans=3. Search Left `[5,7,7]`.
    -   Not found. Ans=3.
2.  Find Last:
    -   Mid `8` (idx 3). Ans=3. Search Right `[8, 10]`.
    -   Mid `8` (idx 4). Ans=4. Search Right `[10]`.
    -   Not found. Ans=4.
Result `[3, 4]`.
