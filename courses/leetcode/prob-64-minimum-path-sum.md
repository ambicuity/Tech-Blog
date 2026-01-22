---
layout: page
title: "64. Minimum Path Sum"
permalink: /courses/leetcode/prob-64-minimum-path-sum/
---

# 64. Minimum Path Sum

## 1. The Question
Given a `m x n` grid filled with non-negative numbers, find a path from top left to bottom right, which minimizes the sum of all numbers along its path.

Note: You can only move either down or right at any point in time.

### Example 1
**Input**: `grid = [[1,3,1],[1,5,1],[4,2,1]]`
**Output**: `7`
**Explanation**: Because the path 1 -> 3 -> 1 -> 1 -> 1 minimizes the sum.

---

## 2. Explanation
DP State: `dp[r][c]` = min path sum to reach `(r, c)`.
`dp[r][c] = grid[r][c] + min(dp[r-1][c], dp[r][c-1])`.
Base cases:
-   `dp[0][0] = grid[0][0]`.
-   Top row: only from left.
-   Left col: only from up.

Can be done in-place.

-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(1)$ (in-place).

---

## 3. Pseudo Code
```text
m, n = rows, cols
for r in 0..m:
    for c in 0..n:
        if r==0 and c==0: continue
        elif r==0: grid[r][c] += grid[r][c-1]
        elif c==0: grid[r][c] += grid[r-1][c]
        else: grid[r][c] += min(grid[r-1][c], grid[r][c-1])
return grid[m-1][n-1]
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def minPathSum(self, grid: list[list[int]]) -> int:
        rows, cols = len(grid), len(grid[0])
        
        for r in range(rows):
            for c in range(cols):
                if r == 0 and c == 0:
                    continue
                elif r == 0:
                    # First row, can only come from left
                    grid[r][c] += grid[r][c-1]
                elif c == 0:
                    # First col, can only come from up
                    grid[r][c] += grid[r-1][c]
                else:
                    # Min of up or left
                    grid[r][c] += min(grid[r-1][c], grid[r][c-1])
                    
        return grid[rows-1][cols-1]
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[[1,3,1], [1,5,1]]`
1.  `(0,0)`: 1.
2.  `(0,1)`: `3+1=4`. `(0,2)`: `1+4=5`.
3.  `(1,0)`: `1+1=2`.
4.  `(1,1)`: `5 + min(4, 2) = 7`.
5.  `(1,2)`: `1 + min(5, 7) = 6`.
Result 6.
(Wait example output is 7 for 3x3. My dry run valid for first 2 rows).
