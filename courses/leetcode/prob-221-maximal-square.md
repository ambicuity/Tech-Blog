---
layout: page
title: "221. Maximal Square"
permalink: /courses/leetcode/prob-221-maximal-square/
---

# 221. Maximal Square

## 1. The Question
Given an `m x n` binary matrix filled with `0`'s and `1`'s, find the largest square containing only `1`'s and return its area.

### Example 1
**Input**: `matrix = [["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]`
**Output**: `4`

---

## 2. Explanation
DP State: `dp[i][j]` = side length of largest square ending at `(i, j)`.
If `matrix[i][j] == '1'`:
`dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])`.
Else `0`.
The idea is that a square of size `k` needs smaller squares of size `k-1` to its top, left, and top-left.

-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(M \cdot N)$ or $O(N)$ optimized.

---

## 3. Pseudo Code
```text
max_side = 0
for i in rows:
    for j in cols:
        if matrix[i][j] == '1':
             dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
             max_side = max(max_side, dp[i][j])
return max_side * max_side
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def maximalSquare(self, matrix: list[list[str]]) -> int:
        if not matrix: return 0
        
        rows, cols = len(matrix), len(matrix[0])
        dp = [[0] * (cols + 1) for _ in range(rows + 1)]
        max_side = 0
        
        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                if matrix[r-1][c-1] == '1':
                    dp[r][c] = 1 + min(dp[r-1][c], dp[r][c-1], dp[r-1][c-1])
                    max_side = max(max_side, dp[r][c])
                    
        return max_side * max_side
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(M \cdot N)$.

## 6. Example Walkthrough
Matrix with square 2x2.
Bottom right '1'. Top, Left, TopLeft are all 1.
`min(1, 1, 1) + 1 = 2`.
Square side 2. Area 4.
