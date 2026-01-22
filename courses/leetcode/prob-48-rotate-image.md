---
layout: page
title: "48. Rotate Image"
permalink: /courses/leetcode/prob-48-rotate-image/
---

# 48. Rotate Image

## 1. The Question
You are given an `n x n` 2D matrix representing an image, rotate the image by **90 degrees (clockwise)**.

You have to rotate the image **in-place**, which means you have to modify the input 2D matrix directly. **DO NOT** allocate another 2D matrix and do the rotation.

### Example 1
![Rotate Image](https://assets.leetcode.com/uploads/2020/08/28/mat1.jpg)
**Input**: `matrix = [[1,2,3],[4,5,6],[7,8,9]]`
**Output**: `[[7,4,1],[8,5,2],[9,6,3]]`

### Example 2
**Input**: `matrix = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]`
**Output**: `[[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]`

---

## 2. Explanation
We need to move elements such that `matrix[i][j]` becomes `matrix[j][n-1-i]`.
Trying to do this cell-by-cell is complicated because we overwrite values we need later.

### Approach 1: Transpose + Reflect (Optimal Magic)
Rotating 90 degrees clockwise is mathematically equivalent to:
1.  **Transpose**: Swap `matrix[i][j]` with `matrix[j][i]`. (Reflect across main diagonal).
2.  **Reflect**: Reverse each row. `matrix[i]` becomes `matrix[i][::-1]`. (Reflect across vertical axis).

Example:
`[[1,2], [3,4]]`
Transpose: `[[1,3], [2,4]]`
Reflect Rows: `[[3,1], [4,2]]` => Rotated 90 deg.

-   **Time**: $O(N^2)$.
-   **Space**: $O(1)$.

### Approach 2: Ring Rotation (Four-Way Swap)
Rotate the outer ring, then the next inner ring.
Process 4 cells at a time in a cycle.
`top-left` -> `top-right` -> `bottom-right` -> `bottom-left` -> `top-left`.
-   **Time**: $O(N^2)$.
-   **Space**: $O(1)$.

We will implement **Approach 1** because it's easier to remember and code correctly during an interview.

---

## 3. Pseudo Code (Transpose + Reflect)
```text
n = length(matrix)

# 1. Transpose
For i from 0 to n-1:
    For j from i+1 to n-1:
        Swap(matrix[i][j], matrix[j][i])

# 2. Reflect (Reverse Rows)
For i from 0 to n-1:
    Reverse(matrix[i])
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def rotate(self, matrix: list[list[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        """
        n = len(matrix)
        
        # 1. Transpose (Swap across diagonal)
        for i in range(n):
            for j in range(i + 1, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
                
        # 2. Reverse each row
        for i in range(n):
            matrix[i].reverse()
```

---

## 5. Complexity
-   **Time**: $O(N^2)$. We visit each cell twice.
-   **Space**: $O(1)$. In-place.

## 6. Example Walkthrough
`[[1,2,3], [4,5,6], [7,8,9]]`

1.  **Transpose**:
    -   Swap(0,1), (1,0): 2, 4 -> `[[1,4,3], [2,5,6], [7,8,9]]`
    -   Swap(0,2), (2,0): 3, 7 -> `[[1,4,7], [2,5,6], [3,8,9]]`
    -   Swap(1,2), (2,1): 6, 8 -> `[[1,4,7], [2,5,8], [3,6,9]]`
    Result: `[[1,4,7], [2,5,8], [3,6,9]]`

2.  **Reverse Rows**:
    -   Row 0: `[7,4,1]`
    -   Row 1: `[8,5,2]`
    -   Row 2: `[9,6,3]`

Final: `[[7,4,1], [8,5,2], [9,6,3]]`. Correct.
