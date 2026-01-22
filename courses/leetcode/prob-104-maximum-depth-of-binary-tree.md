---
layout: page
title: "104. Maximum Depth of Binary Tree"
permalink: /courses/leetcode/prob-104-maximum-depth-of-binary-tree/
---

# 104. Maximum Depth of Binary Tree

## 1. The Question
Given the `root` of a binary tree, return its maximum depth.

A binary tree's **maximum depth** is the number of nodes along the longest path from the root node down to the farthest leaf node.

### Example 1
**Input**: `root = [3,9,20,null,null,15,7]`
**Output**: `3`
**Explanation**: Depth is 3 (3 -> 20 -> 15 or 3 -> 20 -> 7).

### Example 2
**Input**: `root = [1,null,2]`
**Output**: `2`

---

## 2. Explanation
This is a standard tree traversal problem.
We can use Depth First Search (DFS) or Breadth First Search (BFS).

### Approach 1: Recursive DFS
The depth of a node is `1 + max(depth(left), depth(right))`.
Base case: If node is `None`, depth is `0`.

-   **Time**: $O(N)$.
-   **Space**: $O(H)$ (Height of tree) for recursion stack.

### Approach 2: Iterative BFS (Level Order)
Traverse level by level. Increment depth for each level.
-   **Time**: $O(N)$.
-   **Space**: $O(W)$ (Width of tree).

We will use Recursive DFS as it is the most elegant.

---

## 3. Pseudo Code
```text
def maxDepth(root):
    if not root:
        return 0
    
    left_depth = maxDepth(root.left)
    right_depth = maxDepth(root.right)
    
    return 1 + max(left_depth, right_depth)
```

---

## 4. Optimal Code (Python)

```python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
            
        return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`[3,9,20,null,null,15,7]`

1.  `maxDepth(3)` calls `maxDepth(9)` and `maxDepth(20)`.
2.  `maxDepth(9)`: Left=0, Right=0. Return 1.
3.  `maxDepth(20)` calls `maxDepth(15)` and `maxDepth(7)`.
    -   `maxDepth(15)`: Return 1.
    -   `maxDepth(7)`: Return 1.
    -   `maxDepth(20)` returns `1 + max(1, 1) = 2`.
4.  `maxDepth(3)` returns `1 + max(1, 2) = 3`.
