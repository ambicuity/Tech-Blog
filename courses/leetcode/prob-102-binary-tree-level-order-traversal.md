---
layout: page
title: "102. Binary Tree Level Order Traversal"
permalink: /courses/leetcode/prob-102-binary-tree-level-order-traversal/
---

# 102. Binary Tree Level Order Traversal

## 1. The Question
Given the `root` of a binary tree, return the level order traversal of its nodes' values. (i.e., from left to right, level by level).

### Example 1
**Input**: `root = [3,9,20,null,null,15,7]`
**Output**: `[[3],[9,20],[15,7]]`

### Example 2
**Input**: `root = [1]`
**Output**: `[[1]]`

---

## 2. Explanation
This is the textbook BFS problem.
Use a Queue. Iterate level by level.

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
if not root: return []
q = [root]
res = []

while q:
    level = []
    level_size = len(q)
    for i in range(level_size):
        node = q.pop(0)
        level.append(node.val)
        if node.left: q.append(node.left)
        if node.right: q.append(node.right)
    res.append(level)

return res
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
    def levelOrder(self, root: Optional[TreeNode]) -> list[list[int]]:
        if not root:
            return []
            
        result = []
        queue = [root]
        
        while queue:
            level_size = len(queue)
            current_level = []
            
            for _ in range(level_size):
                node = queue.pop(0)
                current_level.append(node.val)
                
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
                    
            result.append(current_level)
            
        return result
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`[3, 9, 20]`

1.  Q:`[3]`. Pop 3. Level:`[3]`. Q:`[9, 20]`.
2.  Q:`[9, 20]`. Pop 9, 20. Level:`[9, 20]`. Q: Empty.
