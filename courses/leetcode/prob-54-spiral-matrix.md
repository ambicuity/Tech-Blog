---
layout: page
title: "54. Spiral Matrix"
permalink: /courses/leetcode/prob-54-spiral-matrix/
---

# 54. Spiral Matrix

## 1. The Question
Given an `m x n` matrix, return all elements of the matrix in spiral order.

### Example 1
![Spiral Matrix](https://assets.leetcode.com/uploads/2020/11/13/spiral1.jpg)
**Input**: `matrix = [[1,2,3],[4,5,6],[7,8,9]]`
**Output**: `[1,2,3,6,9,8,7,4,5]`

### Example 2
**Input**: `matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]`
**Output**: `[1,2,3,4,8,12,11,10,9,5,6,7]`

---

## 2. Explanation
We need to traverse the matrix in layers, layer by layer.
Boundaries: `top`, `bottom`, `left`, `right`.

1.  Traverse **Left -> Right** along `top`. Increment `top`.
2.  Traverse **Top -> Bottom** along `right`. Decrement `right`.
3.  Traverse **Right -> Left** along `bottom`. Decrement `bottom`.
4.  Traverse **Bottom -> Top** along `left`. Increment `left`.
5.  Repeat until boundaries cross.

**Crucial Check**: After every traversal, check if the boundaries have crossed. For example, after traversing top, if `top > bottom`, break.

### Approach: Simulation with Boundaries
-   `top = 0`, `bottom = m-1`.
-   `left = 0`, `right = n-1`.
-   While `top <= bottom` and `left <= right`...

-   **Time**: $O(m \times n)$. Every element visited once.
-   **Space**: $O(1)$ (excluding output).

---

## 3. Pseudo Code
```text
res = []
top = 0, bottom = m - 1
left = 0, right = n - 1

While top <= bottom AND left <= right:
    # 1. Left to Right
    For i from left to right:
        res.append(matrix[top][i])
    top++
    
    # 2. Top to Bottom
    For i from top to bottom:
        res.append(matrix[i][right])
    right--
    
    # Break Check
    If top > bottom OR left > right: Break
    
    # 3. Right to Left
    For i from right down to left:
        res.append(matrix[bottom][i])
    bottom--
    
    # 4. Bottom to Top
    For i from bottom down to top:
        res.append(matrix[i][left])
    left++

Return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def spiralOrder(self, matrix: list[list[int]]) -> list[int]:
        if not matrix:
            return []
            
        res = []
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1
        
        while top <= bottom and left <= right:
            # 1. Traverse Right
            for i in range(left, right + 1):
                res.append(matrix[top][i])
            top += 1
            
            # 2. Traverse Down
            for i in range(top, bottom + 1):
                res.append(matrix[i][right])
            right -= 1
            
            # Check if we are done before traversing back
            if top > bottom or left > right:
                break
                
            # 3. Traverse Left
            for i in range(right, left - 1, -1):
                res.append(matrix[bottom][i])
            bottom -= 1
            
            # 4. Traverse Up
            for i in range(bottom, top - 1, -1):
                res.append(matrix[i][left])
            left += 1
            
        return res
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]`
`T=0, B=2, L=0, R=2`

1.  **Right**: `1, 2, 3`. `T=1`.
2.  **Down**: `6, 9`. `R=1`.
3.  Check: `1 <= 2` and `0 <= 1`. OK.
4.  **Left**: `8, 7`. `B=1`.
5.  **Up**: `4`. `L=1`.
6.  Loop again. `T=1, B=1, L=1, R=1`.
    -   **Right**: `5`. `T=2`.
    -   **Down**: (Range `2` to `1` is empty).
    -   Check: `T(2) > B(1)`. Break.

Result: `[1, 2, 3, 6, 9, 8, 7, 4, 5]`.
