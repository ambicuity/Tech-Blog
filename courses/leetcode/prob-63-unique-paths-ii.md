---
layout: page
title: "63. Unique Paths II"
permalink: /courses/leetcode/prob-63-unique-paths-ii/
---

# 63. Unique Paths II

## 1. The Question
You are given an `m x n` integer array `obstacleGrid`. There is a robot initially located at the top-left corner (i.e., `grid[0][0]`). The robot tries to move to the bottom-right corner (i.e., `grid[m - 1][n - 1]`). The robot can only move either down or right at any point in time.

An obstacle and space are marked as `1` or `0` respectively in `obstacleGrid`. A path that the robot takes cannot include any square that is an obstacle.

Return the number of possible unique paths that the robot can take to reach the bottom-right corner.

### Example 1
**Input**: `obstacleGrid = [[0,0,0],[0,1,0],[0,0,0]]`
**Output**: `2`

---

## 2. Explanation
DP State: `dp[r][c]` = unique paths to `(r, c)`.
If `grid[r][c] == 1` (obstacle), `dp[r][c] = 0`.
Else `dp[r][c] = dp[r-1][c] + dp[r][c-1]`.
Base case: `dp[0][0] = 1` if no obstacle there, else 0.

-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(1)$ (in-place) or $O(N)$ (row optimization).

---

## 3. Pseudo Code
```text
if grid[0][0] == 1: return 0
grid[0][0] = 1

for r in 0..m:
    for c in 0..n:
         if r==0 and c==0: continue
         if grid[r][c] == 1:
             grid[r][c] = 0 # No paths through obstacle
         else:
             from_up = grid[r-1][c] if r>0 else 0
             from_left = grid[r][c-1] if c>0 else 0
             grid[r][c] = from_up + from_left
return grid[m-1][n-1]
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def uniquePathsWithObstacles(self, obstacleGrid: list[list[int]]) -> int:
        if not obstacleGrid or obstacleGrid[0][0] == 1:
            return 0
            
        rows, cols = len(obstacleGrid), len(obstacleGrid[0])
        
        # We can use the grid itself as DP table.
        # However, grid has 1s for obstacles, so we should be careful.
        # Let's verify input format: 1 (obstacle), 0 (space).
        # We'll use negative numbers or just handle logic carefully.
        # Actually easier to use a new DP row for O(N) space.
        
        dp = [0] * cols
        dp[0] = 1 # Start point
        
        for r in range(rows):
            for c in range(cols):
                if obstacleGrid[r][c] == 1:
                    dp[c] = 0
                elif c > 0:
                    dp[c] += dp[c-1]
                    
        return dp[-1]
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`[[0,0,0],[0,1,0],[0,0,0]]`
1.  Init dp `[1, 0, 0]`.
2.  Row 0: `c=1`: `dp[1]+=dp[0]=1`. `c=2`: `dp[2]+=dp[1]=1`. DP: `[1, 1, 1]`.
3.  Row 1: `c=0`: `obs=0`. `c=1`: `obs=1`. `dp[1]=0`. `c=2`: `dp[2]+=dp[1](0)=1`. DP: `[1, 0, 1]`.
4.  Row 2: `c=0`: `dp[0]=1`. `c=1`: `dp[1]+=dp[0]=1`. `c=2`: `dp[2]+=dp[1]=2`. DP: `[1, 1, 2]`.
Result 2.
