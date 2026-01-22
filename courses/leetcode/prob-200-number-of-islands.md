---
layout: page
title: "200. Number of Islands"
permalink: /courses/leetcode/prob-200-number-of-islands/
---

# 200. Number of Islands

## 1. The Question
Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the number of islands.

An **island** is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.

### Example 1
**Input**:
```
grid = [
  ["1","1","1","1","0"],
  ["1","1","0","1","0"],
  ["1","1","0","0","0"],
  ["0","0","0","0","0"]
]
```
**Output**: `1`

### Example 2
**Input**:
```
grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]
```
**Output**: `3`

---

## 2. Explanation
We need to count connected components of '1's.
Iterate through the grid.
1.  If we encounter a '1', it is part of a new island. Increment count.
2.  Start a traversal (DFS or BFS) from that '1' to find all connected '1's and mark them as visited (e.g., set to '0' or '#').
3.  Continue iteration.

-   **Time**: $O(M \cdot N)$. Every cell is visited once.
-   **Space**: $O(M \cdot N)$ in worst case (recursion stack for full grid).

### Approach: Recursive DFS
DFS is generally easier to write for grid connectivity.

---

## 3. Pseudo Code
```text
count = 0
For r in 0..rows:
    For c in 0..cols:
        if grid[r][c] == '1':
            count += 1
            dfs(r, c)

def dfs(r, c):
    if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] != '1':
        return
    
    grid[r][c] = '0' # Mark as visited
    
    dfs(r+1, c)
    dfs(r-1, c)
    dfs(r, c+1)
    dfs(r, c-1)
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def numIslands(self, grid: list[list[str]]) -> int:
        if not grid:
            return 0
            
        rows, cols = len(grid), len(grid[0])
        count = 0
        
        def dfs(r, c):
            # Base case: out of bounds or water
            if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] == '0':
                return
            
            # Mark as visited (sink the island)
            grid[r][c] = '0'
            
            # Visit neighbors
            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)
            
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == '1':
                    count += 1
                    dfs(r, c)
                    
        return count
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(M \cdot N)$ (recursion).

## 6. Example Walkthrough
1.  Find '1' at (0,0). Count=1.
2.  DFS(0,0):
    -   Mark (0,0) -> '0'.
    -   DFS neighbors... recursively marks all connected '1's to '0'.
3.  Continue loop. Next unvisited '1' (if any) starts a new island.
