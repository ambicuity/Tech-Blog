---
layout: page
title: "55. Jump Game"
permalink: /courses/leetcode/prob-55-jump-game/
---

# 55. Jump Game

## 1. The Question
You are given an integer array `nums`. You are initially positioned at the array's **first index**. Each element in the array represents your maximum jump length at that position.

Return `true` if you can reach the last index, or `false` otherwise.

### Example 1
**Input**: `nums = [2,3,1,1,4]`
**Output**: `true`
**Explanation**: Jump 1 step from index 0 to 1, then 3 steps to the last index.

### Example 2
**Input**: `nums = [3,2,1,0,4]`
**Output**: `false`
**Explanation**: You will always arrive at index 3 no matter what. Its maximum jump length is 0, which makes it impossible to reach the last index.

---

## 2. Explanation
This is a classic greedy problem. We don't need to calculate *every* path; we just need to know the **farthest point** we can reach.

### Approach: Greedy
Iterate through the array. Maintain a variable `max_reachable` (the furthest index we can currently reach).

For each index `i`:
1.  **Check if accessible**: If `i > max_reachable`, it means we cannot even reach this step. Return `False`.
2.  **Update Reach**: `max_reachable = max(max_reachable, i + nums[i])`.
3.  **Check Target**: If `max_reachable >= last_index`, return `True` early.
    (Though simpler loop condition acts as implicit check).

---

## 3. Pseudo Code
```text
max_reachable = 0
last_index = length(nums) - 1

For i from 0 to last_index:
    If i > max_reachable:
        Return False
    
    max_reachable = max(max_reachable, i + nums[i])
    
    If max_reachable >= last_index:
        Return True

Return True
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def canJump(self, nums: list[int]) -> bool:
        max_reachable = 0
        last_index = len(nums) - 1
        
        for i, jump in enumerate(nums):
            # If we are at a position we can't reach, game over
            if i > max_reachable:
                return False
            
            # Update the farthest we can reach 
            max_reachable = max(max_reachable, i + jump)
            
            # Optimization: If we can already reach the end
            if max_reachable >= last_index:
                return True
                
        return True
```

---

## 5. Complexity
-   **Time**: $O(n)$. We visit each element once.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`nums = [3, 2, 1, 0, 4]`

1.  `i=0`, `jump=3`. `max_reachable = max(0, 0+3) = 3`.
2.  `i=1`, `jump=2`. `1 <= 3`. `max_reachable = max(3, 1+2) = 3`.
3.  `i=2`, `jump=1`. `2 <= 3`. `max_reachable = max(3, 2+1) = 3`.
4.  `i=3`, `jump=0`. `3 <= 3`. `max_reachable = max(3, 3+0) = 3`.
5.  `i=4`, `jump=4`. `4 > 3`. **Return False**.
