---
layout: page
title: "103. Binary Tree Zigzag Level Order Traversal"
permalink: /courses/leetcode/prob-103-binary-tree-zigzag-level-order-traversal/
---

# 103. Binary Tree Zigzag Level Order Traversal

## 1. The Question
Given the `root` of a binary tree, return the zigzag level order traversal of its nodes' values. (i.e., from left to right, then right to left for the next level and alternate between).

### Example 1
**Input**: `root = [3,9,20,null,null,15,7]`
**Output**: `[[3],[20,9],[15,7]]`

### Example 2
**Input**: `root = [1]`
**Output**: `[[1]]`

---

## 2. Explanation
Standard BFS, but maintain a flag `left_to_right`.
If `left_to_right` is False, reverse the current level list before adding to result.
Or, append to head for `False` case.

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
q = [root]
flag = True
res = []

while q:
    level = []
    size = len(q)
    for _ in size:
        node = q.pop(0)
        level.append(node.val)
        add_children(q)
        
    if not flag:
        level.reverse()
    
    res.append(level)
    flag = !flag
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
    def zigzagLevelOrder(self, root: Optional[TreeNode]) -> list[list[int]]:
        if not root:
            return []
            
        result = []
        queue = [root]
        left_to_right = True
        
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
                    
            if not left_to_right:
                current_level.reverse()
                
            result.append(current_level)
            left_to_right = not left_to_right
            
        return result
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`[3, 9, 20, 15, 7]`

1.  L0: `[3]`. Flag T. Stay `[3]`. Next Flag F.
2.  L1: `[9, 20]`. Flag F. Reverse `[20, 9]`. Next Flag T.
3.  L2: `[15, 7]`. Flag T. Stay `[15, 7]`.
