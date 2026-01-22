---
layout: page
title: "289. Game of Life"
permalink: /courses/leetcode/prob-289-game-of-life/
---

# 289. Game of Life

## 1. The Question
According to Wikipedia's article: "The Game of Life, also known simply as Life, is a cellular automaton devised by the British mathematician John Horton Conway in 1970."

The board is made up of an `m x n` grid of cells, where each cell has an initial state: **live** (represented by a `1`) or **dead** (represented by a `0`). Each cell interacts with its **eight neighbors** (horizontal, vertical, diagonal) using the following four rules:

1.  Any live cell with fewer than two live neighbors dies as if caused by under-population.
2.  Any live cell with two or three live neighbors lives on to the next generation.
3.  Any live cell with more than three live neighbors dies, as if by over-population.
4.  Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction.

The next state is created by applying the above rules simultaneously to every cell in the current state, where births and deaths occur simultaneously. Given the current state of the `m x n` grid `board`, return the next state.

### Example 1
**Input**: `board = [[0,1,0],[0,0,1],[1,1,1],[0,0,0]]`
**Output**: `[[0,0,0],[1,0,1],[0,1,1],[0,1,0]]`

---

## 2. Explanation
We need to update the board based on the neighbor counts.
Challenge: Checking neighbors requires the **old** state, but writing to the board updates it to the **new** state.

### Approach 1: Copy Board
Create a copy `copy_board`. Read from copy, write to `board`.
-   **Space**: $O(M \cdot N)$.

### Approach 2: In-Place State Encoding (Optimal)
We can use extra bits or special values to store both the *old* state and the *new* state in the same cell.
-   Current state: 0 or 1.
-   New state: 0 or 1.
We can define composite states:
-   `0`: Dead -> Dead
-   `1`: Live -> Live
-   `2`: Live -> Dead (Was 1, becomes 0)
-   `3`: Dead -> Live (Was 0, becomes 1)

**Algorithm**:
1.  Iterate through board. Count live neighbors.
    -   (Note: `1` and `2` count as live in old state).
2.  Apply rules:
    -   If Live (`1`) and neighbors < 2 or > 3: State changes to `2` (Live->Dead).
    -   If Dead (`0`) and neighbors == 3: State changes to `3` (Dead->Live).
3.  Iterate again to decoding:
    -   Change `2` to `0`.
    -   Change `3` to `1`.

-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
For r in 0..m:
    For c in 0..n:
        neighbors = count_live_neighbors(r, c) # Count 1s and 2s
        
        If board[r][c] == 1:
            If neighbors < 2 or neighbors > 3:
                board[r][c] = 2 # Live -> Dead
        Else:
            If neighbors == 3:
                board[r][c] = 3 # Dead -> Live

For r in 0..m:
    For c in 0..n:
        If board[r][c] == 2: board[r][c] = 0
        If board[r][c] == 3: board[r][c] = 1
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def gameOfLife(self, board: list[list[int]]) -> None:
        """
        Do not return anything, modify board in-place instead.
        """
        # 0: Dead -> Dead
        # 1: Live -> Live
        # 2: Live -> Dead
        # 3: Dead -> Live
        
        m = len(board)
        n = len(board[0])
        
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for r in range(m):
            for c in range(n):
                live_neighbors = 0
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    
                    if 0 <= nr < m and 0 <= nc < n:
                        # Check if neighbor was live in original state
                        # 1 was live, 2 was live (now dead)
                        if board[nr][nc] == 1 or board[nr][nc] == 2:
                            live_neighbors += 1
                            
                # Apply Rules
                if board[r][c] == 1:
                    # Live cell dies
                    if live_neighbors < 2 or live_neighbors > 3:
                        board[r][c] = 2
                else:
                    # Dead cell revives
                    if live_neighbors == 3:
                        board[r][c] = 3
                        
        # Final pass: Decode
        for r in range(m):
            for c in range(n):
                if board[r][c] == 2:
                    board[r][c] = 0
                elif board[r][c] == 3:
                    board[r][c] = 1
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[[0,1,0], [0,0,1]]`

Cell `(0,1)` is `1`. Neighbors: `(1,2)` is `1`. Count = 1.
Rule: `<2` dies. Set `(0,1)` to `2`.

Cell `(0,2)` is `0`. Neighbors: `(0,1)` was `1`, `(1,2)` is `1`. Count = 2.
No change.

Decode:
`2` becomes `0`.
Result `(0,1)` becomes `0`.
