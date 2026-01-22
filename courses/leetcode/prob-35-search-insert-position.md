---
layout: page
title: "35. Search Insert Position"
permalink: /courses/leetcode/prob-35-search-insert-position/
---

# 35. Search Insert Position

## 1. The Question
Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted in order.

You must write an algorithm with `O(log n)` runtime complexity.

### Example 1
**Input**: `nums = [1,3,5,6], target = 5`
**Output**: `2`

### Example 2
**Input**: `nums = [1,3,5,6], target = 2`
**Output**: `1`

---

## 2. Explanation
Standard Binary Search.
We want to find the first index `i` such that `nums[i] >= target`.
-   If `nums[mid] == target`, returns `mid`.
-   If `nums[mid] < target`, we need to look right. `left = mid + 1`.
-   If `nums[mid] > target`, we need to look left, but `mid` could be the insertion point. `right = mid - 1`.

Finally `left` will point to the insertion position.

-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
l, r = 0, n-1
while l <= r:
    mid = (l + r) // 2
    if nums[mid] == target: return mid
    elif nums[mid] < target: l = mid + 1
    else: r = mid - 1
return l
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def searchInsert(self, nums: list[int], target: int) -> int:
        left, right = 0, len(nums) - 1
        
        while left <= right:
            mid = (left + right) // 2
            
            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
                
        # If not found, left is the insertion point
        return left
```

---

## 5. Complexity
-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[1, 3, 5, 6]`, `target=2`
1.  `l=0, r=3`. `Mid=(0+3)//2=1`. Val `3`.
2.  `3 > 2`. `r = 1 - 1 = 0`.
3.  `l=0, r=0`. `Mid=0`. Val `1`.
4.  `1 < 2`. `l = 0 + 1 = 1`.
5.  `l=1, r=0`. Loop ends. Return `l=1`.
Matches example.
