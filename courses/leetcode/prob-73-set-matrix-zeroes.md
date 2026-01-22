---
layout: page
title: "73. Set Matrix Zeroes"
permalink: /courses/leetcode/prob-73-set-matrix-zeroes/
---

# 73. Set Matrix Zeroes

## 1. The Question
Given an `m x n` integer matrix `matrix`, if an element is `0`, set its entire row and column to `0`'s.

You must do it **in-place**.

### Example 1
**Input**: `matrix = [[1,1,1],[1,0,1],[1,1,1]]`
**Output**: `[[1,0,1],[0,0,0],[1,0,1]]`

### Example 2
**Input**: `matrix = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]`
**Output**: `[[0,0,0,0],[0,4,5,0],[0,3,1,0]]`

---

## 2. Explanation
We need to mark rows and columns for deletion (setting to 0).
The catch: If we set a cell to 0 immediately, we lose the information that it was originally non-zero, potentially causing a chain reaction.

### Approach 1: Extra Space
Use two sets: `zero_rows` and `zero_cols`.
Pass 1: Store indices of all 0s.
Pass 2: Set rows and cols to 0.
-   **Space**: $O(M + N)$.

### Approach 2: Use First Row/Col as Flags (Optimal)
We can store the flags *inside* the matrix itself.
-   Use `matrix[i][0]` to indicate if Row `i` needs to be zeroed.
-   Use `matrix[0][j]` to indicate if Col `j` needs to be zeroed.
-   **Exception**: `matrix[0][0]` represents both Row 0 and Col 0. We need a separate variable for one of them (e.g., `row_zero_flag`).

Algorithm:
1.  Check if Row 0 contains a 0. Set `row_zero = True`.
2.  Check if Col 0 contains a 0. Set `col_zero = True`.
3.  Iterate rest of matrix `(1..m, 1..n)`. If `matrix[i][j] == 0`, set `matrix[i][0] = 0` and `matrix[0][j] = 0`.
4.  Iterate rest of matrix `(1..m, 1..n)` again. If flag `matrix[i][0] == 0` or `matrix[0][j] == 0`, set cell to 0.
5.  If `row_zero`, zero out Row 0.
6.  If `col_zero`, zero out Col 0.

-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
m, n = dims(matrix)
first_row_has_zero = False
first_col_has_zero = False

# 1. Check flags
For c in 0..n: if matrix[0][c] == 0: first_row_has_zero = True
For r in 0..m: if matrix[r][0] == 0: first_col_has_zero = True

# 2. Mark flags in first row/col
For r in 1..m:
    For c in 1..n:
        if matrix[r][c] == 0:
            matrix[r][0] = 0
            matrix[0][c] = 0

# 3. Use flags to zero cells
For r in 1..m:
    For c in 1..n:
        if matrix[r][0] == 0 OR matrix[0][c] == 0:
            matrix[r][c] = 0

# 4. Handle first row/col separately
If first_row_has_zero: Set row 0 to 0
If first_col_has_zero: Set col 0 to 0
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def setZeroes(self, matrix: list[list[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        """
        m = len(matrix)
        n = len(matrix[0])
        
        first_row_zero = False
        first_col_zero = False
        
        # 1. Determine if first row or first col need to be zeroed
        for c in range(n):
            if matrix[0][c] == 0:
                first_row_zero = True
                break
                
        for r in range(m):
            if matrix[r][0] == 0:
                first_col_zero = True
                break
                
        # 2. Use first row and first col as flags
        for r in range(1, m):
            for c in range(1, n):
                if matrix[r][c] == 0:
                    matrix[r][0] = 0
                    matrix[0][c] = 0
                    
        # 3. Zero out cells based on flags
        for r in range(1, m):
            for c in range(1, n):
                if matrix[r][0] == 0 or matrix[0][c] == 0:
                    matrix[r][c] = 0
                    
        # 4. Handle first row and col
        if first_row_zero:
            for c in range(n):
                matrix[0][c] = 0
                
        if first_col_zero:
            for r in range(m):
                matrix[r][0] = 0
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[[1,1,1], [1,0,1], [1,1,1]]`

1.  Row 0 OK. Col 0 OK.
2.  Scan inner: `(1,1)` is 0. Set `m[1][0]=0`, `m[0][1]=0`.
    Matrix: `[[1,0,1], [0,0,1], [1,1,1]]`.
3.  Zero inner:
    -   `(1,1)`: flag `m[1][0]` is 0. Set to 0. (Already 0).
    -   `(1,2)`: flag `m[1][0]` is 0. Set to 0.
    -   `(2,1)`: flag `m[0][1]` is 0. Set to 0.
    Matrix: `[[1,0,1], [0,0,0], [1,0,1]]`.
4.  First row/col flags were False. Done.
    `[[1,0,1], [0,0,0], [1,0,1]]`. Correct.
