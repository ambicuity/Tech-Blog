---
layout: page
title: "1. Two Sum"
permalink: /courses/leetcode/prob-1-two-sum/
---

# 1. Two Sum

## 1. The Question
Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have **exactly one solution**, and you may not use the same element twice.

You can return the answer in any order.

### Example 1
**Input**: `nums = [2,7,11,15], target = 9`
**Output**: `[0,1]`
**Explanation**: Because `nums[0] + nums[1] == 9`, we return `[0, 1]`.

### Example 2
**Input**: `nums = [3,2,4], target = 6`
**Output**: `[1,2]`

### Example 3
**Input**: `nums = [3,3], target = 6`
**Output**: `[0,1]`

---

## 2. Explanation
We need to find indices `i, j` such that `nums[i] + nums[j] == target`.

### Approach: Hash Map (One Pass)
Iterate through the array. For each element `num`:
1.  Calculate `complement = target - num`.
2.  Check if `complement` exists in our hash map.
    -   If yes, we found the pair! Return `[map[complement], current_index]`.
    -   If no, add `num` to the map: `map[num] = current_index`.

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
map = {}

For i, num in enumerate(nums):
    complement = target - num
    
    If complement in map:
        Return [map[complement], i]
        
    map[num] = i
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        # Map val -> index
        seen = {}
        
        for i, num in enumerate(nums):
            complement = target - num
            
            if complement in seen:
                return [seen[complement], i]
                
            seen[num] = i
            
        return []
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`nums = [2, 7, 11, 15], target = 9`

1.  `i=0, num=2`. `comp = 7`. Not in map. `map = {2: 0}`.
2.  `i=1, num=7`. `comp = 2`. In map!
    -   Return `[map[2], 1]` -> `[0, 1]`.
