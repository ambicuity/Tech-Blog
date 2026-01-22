---
layout: page
title: "74. Search a 2D Matrix"
permalink: /courses/leetcode/prob-74-search-a-2d-matrix/
---

# 74. Search a 2D Matrix

## 1. The Question
You are given an `m x n` integer matrix `matrix` with the following two properties:
1.  Each row is sorted in non-decreasing order.
2.  The first integer of each row is greater than the last integer of the previous row.

Given an integer `target`, return `true` if `target` is in `matrix` or `false` otherwise.

You must write a solution in `O(log(m * n))` time complexity.

### Example 1
**Input**: `matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3`
**Output**: `true`

---

## 2. Explanation
The matrix is sorted. If we flatten it row by row, it's a single sorted array.
We can Binary Search on the virtual flattened array indices `0` to `m*n - 1`.
Index mapping:
-   `row = index // n`
-   `col = index % n`

-   **Time**: $O(\log(MN))$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
m, n = rows, cols
l, r = 0, m*n - 1

while l <= r:
    mid = (l+r)//2
    val = matrix[mid // n][mid % n]
    if val == target: return True
    elif val < target: l = mid + 1
    else: r = mid - 1
return False
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def searchMatrix(self, matrix: list[list[int]], target: int) -> bool:
        if not matrix:
            return False
            
        rows, cols = len(matrix), len(matrix[0])
        left, right = 0, rows * cols - 1
        
        while left <= right:
            mid = (left + right) // 2
            
            # Map index to 2D coordinates
            r, c = divmod(mid, cols)
            val = matrix[r][c]
            
            if val == target:
                return True
            elif val < target:
                left = mid + 1
            else:
                right = mid - 1
                
        return False
```

---

## 5. Complexity
-   **Time**: $O(\log(MN))$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[[1,3,5,7],[10...]]`, `target=3`. `M=3, N=4`. Size 12.
1.  `l=0, r=11`. `Mid=5`. `5 // 4 = 1`, `5 % 4 = 1`. `matrix[1][1] = 11`.
2.  `11 > 3`. `r = 4`.
3.  `l=0, r=4`. `Mid=2`. `0, 2`. `matrix[0][2] = 5`.
4.  `5 > 3`. `r = 1`.
5.  `l=0, r=1`. `Mid=0`. `0, 0`. `matrix[0][0] = 1`.
6.  `1 < 3`. `l = 1`.
7.  `l=1, r=1`. `Mid=1`. `0, 1`. `matrix[0][1] = 3`.
8.  `3 == 3`. Return True.
