---
layout: page
title: "189. Rotate Array"
permalink: /courses/leetcode/prob-189-rotate-array/
---

# 189. Rotate Array

## 1. The Question
Given an integer array `nums`, rotate the array to the right by `k` steps, where `k` is non-negative.

### Example 1
**Input**: `nums = [1,2,3,4,5,6,7], k = 3`
**Output**: `[5,6,7,1,2,3,4]`
**Explanation**:
rotate 1 steps to the right: `[7,1,2,3,4,5,6]`
rotate 2 steps to the right: `[6,7,1,2,3,4,5]`
rotate 3 steps to the right: `[5,6,7,1,2,3,4]`

### Example 2
**Input**: `nums = [-1,-100,3,99], k = 2`
**Output**: `[3,99,-1,-100]`

---

## 2. Explanation
We need to shift elements to the right. The simplest approach uses an extra array, copying elements to their new position `(i + k) % n`. However, that takes $O(n)$ space.

### Approach 1: Extra Array (Not In-Place)
Create `new_arr` of size `n`. Place `nums[i]` at `new_arr[(i + k) % n]`.  
Copy back to `nums`.
-   **Time**: $O(n)$
-   **Space**: $O(n)$

### Approach 2: Cyclical Replacements
Move numbers cyclically. This is tricky to get right with cycle detection.
-   **Time**: $O(n)$
-   **Space**: $O(1)$

### Approach 3: Reverse (Optimal)
This is the standard "trick" for rotation.
1.  Reverse the **entire** array.
2.  Reverse the first `k` elements.
3.  Reverse the remaining `n-k` elements.

**Why works?**
Original: `[1 2 3 4 5 6 7]`, `k=3`
Reverse All: `[7 6 5 4 3 2 1]`
Reverse `0` to `k-1` (`7,6,5`): `[5 6 7 4 3 2 1]`
Reverse `k` to `n-1` (`4,3,2,1`): `[5 6 7 1 2 3 4]` -> **Done!**

---

## 3. Pseudo Code (Reverse Approach)
```text
n = length(nums)
k = k % n  (handle case where k > n)

Function reverse(start, end):
    while start < end:
        swap(nums[start], nums[end])
        start++, end--

reverse(0, n-1)     // Reverse All
reverse(0, k-1)     // Reverse First part
reverse(k, n-1)     // Reverse Second part
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def rotate(self, nums: list[int], k: int) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        n = len(nums)
        k = k % n  # Important if k > length
        
        # Helper function to reverse a portion of the array
        def reverse(start, end):
            while start < end:
                nums[start], nums[end] = nums[end], nums[start]
                start += 1
                end -= 1
        
        # 1. Reverse the whole array
        reverse(0, n - 1)
        
        # 2. Reverse the first k elements
        reverse(0, k - 1)
        
        # 3. Reverse the rest
        reverse(k, n - 1)
```

---

## 5. Complexity
-   **Time**: $O(n)$. We touch each element twice (once in full reverse, once in partial reverse).
-   **Space**: $O(1)$. In-place modification.

## 6. Example Walkthrough
`nums = [-1, -100, 3, 99]`, `k = 2`
`n = 4`, `k = 2 % 4 = 2`

1.  **Reverse All (0 to 3)**:
    `[99, 3, -100, -1]`
2.  **Reverse First Part (0 to 1 -> indices 0,1)**:
    Reverse `[99, 3]` -> `[3, 99]`
    Array: `[3, 99, -100, -1]`
3.  **Reverse Second Part (2 to 3 -> indices 2,3)**:
    Reverse `[-100, -1]` -> `[-1, -100]`
    Array: `[3, 99, -1, -100]`

Result: `[3, 99, -1, -100]` (Correct)
