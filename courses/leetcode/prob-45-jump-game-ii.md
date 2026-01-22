---
layout: page
title: "45. Jump Game II"
permalink: /courses/leetcode/prob-45-jump-game-ii/
---

# 45. Jump Game II

## 1. The Question
You are given a 0-indexed array of integers `nums` of length `n`. You are initially positioned at `nums[0]`.

Each element `nums[i]` represents the maximum length of a forward jump from index `i`.

Return the **minimum number of jumps** to reach `nums[n - 1]`. The test cases are generated such that you can reach `nums[n - 1]`.

### Example 1
**Input**: `nums = [2,3,1,1,4]`
**Output**: `2`
**Explanation**: The minimum number of jumps to reach the last index is 2. Jump 1 step from index 0 to 1, then 3 steps to the last index.

### Example 2
**Input**: `nums = [2,3,0,1,4]`
**Output**: `2`

---

## 2. Explanation
This is a "Breadth-First Search" (BFS) problem disguised as an array problem. We want to find the shortest path in an unweighted graph (where edges are jumps).

However, we don't need a full queue. We can process the array in "windows" or "levels".
-   **Jump 1**: Range reachable from index 0.
-   **Jump 2**: Range reachable from any index in the Jump 1 range.
-   **Jump 3**: Range reachable from any index in the Jump 2 range.

Two pointers are enough:
-   `current_end`: The end of the current jump range.
-   `farthest`: The farthest index reachable from all points visited so far.

Iterate through the array. Update `farthest`. When we reach `current_end`, it means we **must** have taken a jump to go further. Increment `jumps` and update `current_end` to `farthest`.

---

## 3. Pseudo Code
```text
jumps = 0
current_end = 0
farthest = 0

For i from 0 to n - 2:  (Don't need to jump FROM the last element)
    farthest = max(farthest, i + nums[i])
    
    If i == current_end:
        jumps++
        current_end = farthest
        
Return jumps
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def jump(self, nums: list[int]) -> int:
        n = len(nums)
        if n < 2:
            return 0
            
        jumps = 0
        current_end = 0
        farthest = 0
        
        # We iterate up to n-2 because if we are at n-1, we are already there.
        for i in range(n - 1):
            farthest = max(farthest, i + nums[i])
            
            # If we have reached the end of the current jump "level"
            if i == current_end:
                jumps += 1
                current_end = farthest
                
                # Optimization: If the current level already reaches the end
                if current_end >= n - 1:
                    break
                    
        return jumps
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`nums = [2, 3, 1, 1, 4]`

1.  `i=0`, `nums[0]=2`. `farthest = max(0, 0+2) = 2`.
    -   `i == current_end` (0). `jumps = 1`. `current_end = 2`.
2.  `i=1`, `nums[1]=3`. `farthest = max(2, 1+3) = 4`.
    -   `i != current_end`.
3.  `i=2`, `nums[2]=1`. `farthest = max(4, 2+1) = 4`.
    -   `i == current_end` (2). `jumps = 2`. `current_end = 4`.
    -   `current_end >= 4` -> Break.

Result: 2 jumps.
