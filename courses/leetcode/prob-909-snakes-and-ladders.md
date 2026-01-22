---
layout: page
title: "909. Snakes and Ladders"
permalink: /courses/leetcode/prob-909-snakes-and-ladders/
---

# 909. Snakes and Ladders

## 1. The Question
You are given an `n x n` integer matrix `board` where the cells are labeled from `1` to `n^2` in a **Boustrophedon** style starting from the bottom left of the board (i.e. `board[n - 1][0]`) and alternating direction each row.

You start on square `1` of the board. In each move, starting from square `curr`, do the following:
-   Choose a destination square `next` with a label in the range `[curr + 1, min(curr + 6, n^2)]`.
-   If `board[next]` has a snake or ladder, you **must** move to the destination of that snake or ladder. Otherwise, you move to `next`.
-   The game ends when you reach the square `n^2`.

Return the least number of moves required to reach the square `n^2`. If it is not possible to reach the square, return `-1`.

### Example 1
**Input**:
`board = [[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,35,-1,-1,13,-1],[-1,-1,-1,-1,-1,-1],[-1,15,-1,-1,-1,-1]]`
**Output**: `4`

---

## 2. Explanation
This is a shortest path problem on a graph. The nodes are `1` to `n*n`.
The edges are determined by dice rolls (1 to 6) and special jumps (snakes/ladders).
Since edge weights are 1 (one move), BFS is suitable.

**Coordinate Mapping**:
We need a function `get_pos(num)` that returns `(row, col)` for a given number `num`.
-   Row from bottom: `(num - 1) // n`.
-   Actual row index: `n - 1 - row_from_bottom`.
-   Col:
    -   If `row_from_bottom` is even (0, 2...): Left to Right. `col = (num - 1) % n`.
    -   If `row_from_bottom` is odd (1, 3...): Right to Left. `col = n - 1 - ((num - 1)%n)`.

**BFS**:
1.  Queue: `[(1, 0)]` (curr number, moves). Visited set `{1}`.
2.  Pop `curr`. Loop `die` 1 to 6.
3.  `next_sq = curr + die`.
4.  Get board value at `next_sq`.
    -   If `board[r][c] != -1`, `next_sq = board[r][c]` (Jump).
5.  If `next_sq == n*n`, return `moves + 1`.
6.  If `next_sq` not visited, push to queue.

-   **Time**: $O(N^2)$.
-   **Space**: $O(N^2)$.

---

## 3. Pseudo Code
```text
n = len(board)
end = n * n

def get_coords(num):
    r_up = (num - 1) // n
    c_idx = (num - 1) % n
    r = n - 1 - r_up
    c = c_idx if (r_up % 2 == 0) else (n - 1 - c_idx)
    return r, c

queue = [(1, 0)]
visited = {1}

while queue:
    curr, dist = queue.pop(0)
    for i in 1..6:
        next_curr = curr + i
        if next_curr > end: break
        
        r, c = get_coords(next_curr)
        dest = board[r][c]
        if dest != -1:
            next_curr = dest
            
        if next_curr == end: return dist + 1
        
        if next_curr not in visited:
            visited.add(next_curr)
            queue.append((next_curr, dist + 1))

return -1
```

---

## 4. Optimal Code (Python)

```python
from collections import deque

class Solution:
    def snakesAndLadders(self, board: list[list[int]]) -> int:
        n = len(board)
        target = n * n
        
        def get_coordinates(sq):
            # 0-based row from bottom
            r_from_bottom = (sq - 1) // n
            c_offset = (sq - 1) % n
            
            # Row index in board
            r = n - 1 - r_from_bottom
            
            # Col index depends on direction
            if r_from_bottom % 2 == 0:
                # Even rows (from bottom): Left to Right
                c = c_offset
            else:
                # Odd rows: Right to Left
                c = n - 1 - c_offset
                
            return r, c
            
        queue = deque([(1, 0)])  # (square, moves)
        visited = {1}
        
        while queue:
            curr, moves = queue.popleft()
            
            # Try all dice moves
            for i in range(1, 7):
                next_sq_candidate = curr + i
                
                if next_sq_candidate > target:
                    break
                    
                r, c = get_coordinates(next_sq_candidate)
                
                # If there's a snake or ladder, we MUST generate the destination.
                # If -1, we stay at candidate.
                destination = board[r][c] if board[r][c] != -1 else next_sq_candidate
                
                if destination == target:
                    return moves + 1
                
                if destination not in visited:
                    visited.add(destination)
                    queue.append((destination, moves + 1))
                    
        return -1
```

---

## 5. Complexity
-   **Time**: $O(N^2)$.
-   **Space**: $O(N^2)$.

## 6. Example Walkthrough
Board size 6 (1 to 36).
1.  Start 1. Moves 0.
2.  Next: 2, 3, 4, 5, 6, 7.
3.  Say 2 is Ladder to 15. Queue 15 (Moves 1).
4.  If one path reaches 36, return.
