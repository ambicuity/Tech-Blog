---
layout: page
title: "427. Construct Quad Tree"
permalink: /courses/leetcode/prob-427-construct-quad-tree/
---

# 427. Construct Quad Tree

## 1. The Question
Given a `n * n` matrix `grid` of `0`'s and `1`'s only. We want to represent the `grid` with a Quad-Tree.

Usually, the process is recursive:
1.  If the current grid has the same value (i.e all `1`'s or all `0`'s) set `isLeaf` True and `val` to the value of the grid and set the four children to Null and stop.
2.  If the current grid has different values, set `isLeaf` to False and set `val` to any value and divide the current grid into four sub-grids as shown below.
3.  Recurse for each of the children with the proper sub-grid.

The four children are `topLeft`, `topRight`, `bottomLeft`, `bottomRight`.

### Example 1
**Input**: `grid = [[0,1],[1,0]]`
**Output**: `[[0,1],[1,0],[1,1],[1,1],[1,0]]`
**Explanation**: Standard Quad-Tree representation.

---

## 2. Explanation
This is a straightforward recursion problem.
`build(r, c, size)`:
1.  Check if all elements in the square `[r, r+size)` x `[c, c+size)` are the same.
2.  If yes, return Leaf Node.
3.  If no, split `size // 2`. Create 4 children. Return Parent Node.

**Optimization**:
Checking "all same" takes $O(N^2)$. Total time $O(N^2 \cdot \log N)$?
Better: Just recurse. If 4 children are leaves and have the same value, merge them into one leaf.
This is bottom-up merging.
-   **Time**: $O(N^2)$. each cell visited once.
-   **Space**: $O(\log N)$ stack.

---

## 3. Pseudo Code
```text
def construct(grid):
    def build(r, c, n):
        if n == 1:
            return Node(grid[r][c] == 1, True)
            
        half = n // 2
        tl = build(r, c, half)
        tr = build(r, c+half, half)
        bl = build(r+half, c, half)
        br = build(r+half, c+half, half)
        
        if tl.isLeaf and tr.isLeaf and bl.isLeaf and br.isLeaf and \
           tl.val == tr.val == bl.val == br.val:
            return Node(tl.val, True)
            
        return Node(val=True, isLeaf=False, topLeft=tl, topRight=tr, bottomLeft=bl, bottomRight=br)
        
    return build(0, 0, len(grid))
```

---

## 4. Optimal Code (Python)

```python
"""
# Definition for a QuadTree node.
class Node:
    def __init__(self, val, isLeaf, topLeft, topRight, bottomLeft, bottomRight):
        self.val = val
        self.isLeaf = isLeaf
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
"""

class Solution:
    def construct(self, grid: list[list[int]]) -> 'Node':
        n = len(grid)
        
        def build(r, c, size):
            # Base case: 1x1 grid
            if size == 1:
                return Node(grid[r][c] == 1, True, None, None, None, None)
            
            half = size // 2
            
            topLeft = build(r, c, half)
            topRight = build(r, c + half, half)
            bottomLeft = build(r + half, c, half)
            bottomRight = build(r + half, c + half, half)
            
            # Check if we can merge (all children are leaves and have same value)
            if (topLeft.isLeaf and topRight.isLeaf and 
                bottomLeft.isLeaf and bottomRight.isLeaf and
                topLeft.val == topRight.val == bottomLeft.val == bottomRight.val):
                
                # Merge into one leaf
                return Node(topLeft.val, True, None, None, None, None)
            
            # Cannot merge, return internal node
            # Value can be anything (usually True/1)
            return Node(True, False, topLeft, topRight, bottomLeft, bottomRight)
            
        return build(0, 0, n)
```

---

## 5. Complexity
-   **Time**: $O(N^2)$.
-   **Space**: $O(\log N)$.

## 6. Example Walkthrough
`[[0, 1], [1, 0]]` (Size 2)
1.  TopLeft `0,0` (size 1) -> Leaf(0).
2.  TopRight `0,1` (size 1) -> Leaf(1).
3.  BottomLeft -> Leaf(1).
4.  BottomRight -> Leaf(0).
5.  Check merge: Values `0, 1, 1, 0`. Not same.
6.  Return Internal Node.
