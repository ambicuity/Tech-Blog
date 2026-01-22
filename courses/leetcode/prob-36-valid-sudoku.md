---
layout: page
title: "36. Valid Sudoku"
permalink: /courses/leetcode/prob-36-valid-sudoku/
---

# 36. Valid Sudoku

## 1. The Question
Determine if a `9 x 9` Sudoku board is valid. Only the filled cells need to be validated according to the following rules:

1.  Each row must contain the digits `1-9` without repetition.
2.  Each column must contain the digits `1-9` without repetition.
3.  Each of the nine `3 x 3` sub-boxes of the grid must contain the digits `1-9` without repetition.

Note:
-   A Sudoku board (partially filled) could be valid but is not necessarily solvable.
-   Only the filled cells need to be validated according to the mentioned rules.

### Example 1
**Input**:
```
board = 
[["5","3",".",".","7",".",".",".","."]
,["6",".",".","1","9","5",".",".","."]
,[".","9","8",".",".",".",".","6","."]
,["8",".",".",".","6",".",".",".","3"]
,["4",".",".","8",".","3",".",".","1"]
,["7",".",".",".","2",".",".",".","6"]
,[".","6",".",".",".",".","2","8","."]
,[".",".",".","4","1","9",".",".","5"]
,[".",".",".",".","8",".",".","7","9"]]
```
**Output**: `true`

---

## 2. Explanation
We need to check three conditions for every cell `(r, c)` that has a number:
1.  Is the number unique in Row `r`?
2.  Is the number unique in Column `c`?
3.  Is the number unique in the Box `(r//3, c//3)`?

### Approach: Hash Sets
We can iterate through the entire board once (one pass).
Maintain sets for each row, each column, and each box.
-   `rows[9]` -> Sets
-   `cols[9]` -> Sets
-   `boxes[3][3]` -> Sets

For each cell `board[i][j]`:
-   If it's `'.'`, skip.
-   Check if `num` is in `rows[i]`, `cols[j]`, or `boxes[i//3][j//3]`.
    -   If yes, return `False`.
    -   If no, add to all three sets.

-   **Time**: $O(9 \times 9) = O(1)$. The board size is fixed.
-   **Space**: $O(9 \times 9)$.

---

## 3. Pseudo Code
```text
rows = [Set() for _ in 0..8]
cols = [Set() for _ in 0..8]
boxes = [Set() for _ in 0..8] # or 3x3

For r from 0 to 8:
    For c from 0 to 8:
        val = board[r][c]
        if val == '.': continue
        
        box_idx = (r // 3) * 3 + (c // 3)
        
        If val in rows[r] or val in cols[c] or val in boxes[box_idx]:
            Return False
            
        Add val to rows[r], cols[c], boxes[box_idx]

Return True
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def isValidSudoku(self, board: list[list[str]]) -> bool:
        # Sets to store seen numbers
        rows = [set() for _ in range(9)]
        cols = [set() for _ in range(9)]
        boxes = [set() for _ in range(9)]
        
        for r in range(9):
            for c in range(9):
                val = board[r][c]
                
                if val == '.':
                    continue
                    
                # Calculate box index (0 to 8)
                # Box (0,0) is 0, (0,1) is 1... (2,2) is 8
                box_idx = (r // 3) * 3 + (c // 3)
                
                if val in rows[r] or val in cols[c] or val in boxes[box_idx]:
                    return False
                    
                rows[r].add(val)
                cols[c].add(val)
                boxes[box_idx].add(val)
                
        return True
```

---

## 5. Complexity
-   **Time**: $O(N^2)$ where $N=9$. Since $N$ is fixed, it is $O(1)$.
-   **Space**: $O(N^2)$ to store the sets.

## 6. Example Walkthrough
`board[0][0] = '5'`
-   `rows[0]` adds '5'.
-   `cols[0]` adds '5'.
-   `boxes[0]` adds '5'.

`board[0][1] = '3'`
-   `rows[0]` adds '3'.
-   `cols[1]` adds '3'.
-   `boxes[0]` adds '3'.

If we later find `board[0][4] = '5'`:
-   `rows[0]` already has '5'. -> **Return False**.
