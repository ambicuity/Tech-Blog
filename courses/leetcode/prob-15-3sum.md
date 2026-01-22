---
layout: page
title: "15. 3Sum"
permalink: /courses/leetcode/prob-15-3sum/
---

# 15. 3Sum

## 1. The Question
Given an integer array `nums`, return all the triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.

Notice that the solution set must not contain duplicate triplets.

### Example 1
**Input**: `nums = [-1,0,1,2,-1,-4]`
**Output**: `[[-1,-1,2],[-1,0,1]]`
**Explanation**:
nums[0] + nums[1] + nums[2] = (-1) + 0 + 1 = 0.
nums[1] + nums[2] + nums[4] = 0 + 1 + (-1) = 0.
nums[0] + nums[3] + nums[4] = (-1) + 2 + (-1) = 0.
The distinct triplets are `[-1,0,1]` and `[-1,-1,2]`.

### Example 2
**Input**: `nums = [0,1,1]`
**Output**: `[]`
**Explanation**: The only possible triplet does not sum up to 0.

---

## 2. Explanation
We need to find $a + b + c = 0$. This is equivalent to finding $b + c = -a$.
This reduces the problem to: For each number `nums[i]`, find two other numbers that sum to `-nums[i]`. This is exactly the **Two Sum II** problem (if the array is sorted).

### Approach: Sort + Two Pointers
1.  **Sort** the array. This allows us to use Two Pointers and easily handle duplicates.
2.  Iterate `i` from `0` to `n-3`. This `nums[i]` is our fixed "first number".
3.  Use Two Pointers (`left = i+1`, `right = n-1`) to find pairs that sum to `-nums[i]`.
4.  **Handling Duplicates**:
    -   If `nums[i] == nums[i-1]`, skip iteration to avoid duplicate triplets starting with same number.
    -   When a match is found, move `left` and `right` inward. Also Skip any further duplicates for `left` and `right`.

-   **Time**: $O(n^2)$. Sorting is $O(n \lg n)$. The loop runs $n$ times, and inside is $O(n)$ pointer movement.
-   **Space**: $O(1)$ (or $O(n)$ for sorting depending on implementation).

---

## 3. Pseudo Code
```text
Sort nums
res = []

For i from 0 to n-3:
    If i > 0 AND nums[i] == nums[i-1]: Continue  # Skip duplicate i

    target = -nums[i]
    left = i + 1
    right = n - 1
    
    While left < right:
        sum = nums[left] + nums[right]
        
        If sum == target:
            res.append([nums[i], nums[left], nums[right]])
            left++, right--
            
            # Skip duplicate lefts
            While left < right AND nums[left] == nums[left-1]: left++
            
        Else If sum < target:
            left++
        Else:
            right--

Return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        nums.sort()
        res = []
        n = len(nums)
        
        for i in range(n - 2):
            # Skip duplicates for the first element
            if i > 0 and nums[i] == nums[i-1]:
                continue
                
            # Two Sum II Logic
            target = -nums[i]
            left = i + 1
            right = n - 1
            
            while left < right:
                current_sum = nums[left] + nums[right]
                
                if current_sum == target:
                    res.append([nums[i], nums[left], nums[right]])
                    
                    left += 1
                    right -= 1
                    
                    # Skip duplicates for the second element
                    # (No need to check right separately, logic handles it)
                    while left < right and nums[left] == nums[left-1]:
                        left += 1
                        
                elif current_sum < target:
                    left += 1
                else:
                    right -= 1
                    
        return res
```

---

## 5. Complexity
-   **Time**: $O(n^2)$.
-   **Space**: $O(1)$ (ignoring output).

## 6. Example Walkthrough
`nums = [-1, 0, 1, 2, -1, -4]`
Sort: `[-4, -1, -1, 0, 1, 2]`

1.  `i=0`, `val=-4`. Target `4`.
    -   `L=-1`, `R=2`. Sum=1 < 4. `L++`.
    -   ... No solution for -4.
2.  `i=1`, `val=-1`. Target `1`.
    -   `L=-1` (idx 2), `R=2` (idx 5). Sum `1`. Match! `[-1, -1, 2]`.
    -   `L++` to 0. `R--` to 1.
    -   `L=0` (idx 3), `R=1` (idx 4). Sum `1`. Match! `[-1, 0, 1]`.
3.  `i=2`, `val=-1`. Skip (Duplicate).
4.  `i=3`, `val=0`. Target `0`.
    -   `L=1`, `R=2`. Sum `3` > 0. `R--`.
    -   `L=1`, `R=1`. Stop.

Result: `[[-1, -1, 2], [-1, 0, 1]]`.
