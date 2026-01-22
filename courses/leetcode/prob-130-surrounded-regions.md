---
layout: page
title: "130. Surrounded Regions"
permalink: /courses/leetcode/prob-130-surrounded-regions/
---

# 130. Surrounded Regions

## 1. The Question
Given an `m x n` matrix `board` containing `'X'` and `'O'`, capture all regions that are 4-directionally **surrounded by** `'X'`.

A region is captured by flipping all `'O'`s into `'X'`s in that surrounded region.
Essentially, any 'O' that is not connected to the boundary of the board should be flipped.

### Example 1
**Input**:
```
board = [
["X","X","X","X"],
["X","O","O","X"],
["X","X","O","X"],
["X","O","X","X"]
]
```
**Output**:
```
[
["X","X","X","X"],
["X","X","X","X"],
["X","X","X","X"],
["X","O","X","X"]
]
```
**Explanation**: The 'O's at (1,1), (1,2), (2,2) are surrounded. The 'O' at (3,1) is on the border, so it's not surrounded.

---

## 2. Explanation
We need to find 'O's that **cannot** reach the boundary.
It's easier to find 'O's that **can** reach the boundary and mark them as safe.

### Approach: Boundary DFS
1.  Iterate through the **border** cells of the board.
2.  If a border cell is 'O', run DFS/BFS to find all connected 'O's.
3.  Mark these safe 'O's with a temporary character (e.g., 'T').
4.  After scanning borders, iterate the whole board:
    -   If cell is 'O' (wasn't marked safe), flip to 'X'.
    -   If cell is 'T' (was marked safe), flip back to 'O'.

-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(M \cdot N)$ (recursion).

---

## 3. Pseudo Code
```text
rows, cols
# 1. Mark border connected 'O's as 'T'
for r in rows:
    dfs(r, 0)
    dfs(r, cols-1)
for c in cols:
    dfs(0, c)
    dfs(rows-1, c)

def dfs(r, c):
    if out_of_bounds or board[r][c] != 'O': return
    board[r][c] = 'T'
    dfs neighbors...

# 2. Iterate board
For r in rows:
    For c in cols:
        if board[r][c] == 'O': board[r][c] = 'X'
        if board[r][c] == 'T': board[r][c] = 'O'
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def solve(self, board: list[list[str]]) -> None:
        """
        Do not return anything, modify board in-place instead.
        """
        if not board:
            return
            
        rows, cols = len(board), len(board[0])
        
        def dfs(r, c):
            if r < 0 or c < 0 or r >= rows or c >= cols or board[r][c] != 'O':
                return
            
            # Mark as safe
            board[r][c] = 'T'
            
            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)
            
        # 1. Run DFS from all "O"s on the border
        for r in range(rows):
            dfs(r, 0)
            dfs(r, cols - 1)
            
        for c in range(cols):
            dfs(0, c)
            dfs(rows - 1, c)
            
        # 2. Flip
        for r in range(rows):
            for c in range(cols):
                if board[r][c] == 'O':
                    board[r][c] = 'X' # Captured
                elif board[r][c] == 'T':
                    board[r][c] = 'O' # Safe
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(M \cdot N)$.

## 6. Example Walkthrough
`board` with center 'O's and border 'O's.
1.  DFS from border 'O's marks them 'T'. Connected internal 'O's become 'T'.
2.  Isolated internal 'O's remain 'O'.
3.  Final sweep: 'O' -> 'X', 'T' -> 'O'. Correct.
