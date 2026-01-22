---
layout: page
title: "120. Triangle"
permalink: /courses/leetcode/prob-120-triangle/
---

# 120. Triangle

## 1. The Question
Given a `triangle` array, return the minimum path sum from top to bottom.

For each step, you may move to an adjacent number of the row below. More formally, if you are on index `i` on the current row, you may move to either index `i` or index `i + 1` on the next row.

### Example 1
**Input**: `triangle = [[2],[3,4],[6,5,7],[4,1,8,3]]`
**Output**: `11`
**Explanation**: The triangle looks like:
   2
  3 4
 6 5 7
4 1 8 3
The minimum path sum from top to bottom is 2 + 3 + 5 + 1 = 11.

---

## 2. Explanation
DP approach (Bottom-Up):
Start from the second to last row.
For each element `triangle[r][c]`, the minimum path sum starting from this element to the bottom is:
`triangle[r][c] + min(dp[r+1][c], dp[r+1][c+1])`.
We can modify the triangle in-place.
The top element `triangle[0][0]` will hold the result.

-   **Time**: $O(N^2)$ (total elements).
-   **Space**: $O(1)$ (in-place) or $O(N)$ (if using aux array).

---

## 3. Pseudo Code
```text
for r from n-2 down to 0:
    for c from 0 to len(triangle[r])-1:
        triangle[r][c] += min(triangle[r+1][c], triangle[r+1][c+1])
return triangle[0][0]
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def minimumTotal(self, triangle: list[list[int]]) -> int:
        n = len(triangle)
        
        # Start from the second to last row and move up
        for r in range(n - 2, -1, -1):
            for c in range(len(triangle[r])):
                # For each cell, add the minimum of the two possible children
                triangle[r][c] += min(triangle[r+1][c], triangle[r+1][c+1])
        
        return triangle[0][0]
```

---

## 5. Complexity
-   **Time**: $O(N^2)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[[2], [3,4], [6,5,7], [4,1,8,3]]`
1.  Row 2:
    -   `6`: `6 + min(4, 1) = 7`.
    -   `5`: `5 + min(1, 8) = 6`.
    -   `7`: `7 + min(8, 3) = 10`.
    Triangle: `[[2], [3,4], [7,6,10], ...]`
2.  Row 1:
    -   `3`: `3 + min(7, 6) = 9`.
    -   `4`: `4 + min(6, 10) = 10`.
    Triangle: `[[2], [9,10], ...]`
3.  Row 0:
    -   `2`: `2 + min(9, 10) = 11`.
Result 11.
