---
layout: page
title: "226. Invert Binary Tree"
permalink: /courses/leetcode/prob-226-invert-binary-tree/
---

# 226. Invert Binary Tree

## 1. The Question
Given the `root` of a binary tree, invert the tree, and return its root.

### Example 1
**Input**: `root = [4,2,7,1,3,6,9]`
**Output**: `[4,7,2,9,6,3,1]`

### Example 2
**Input**: `root = [2,1,3]`
**Output**: `[2,3,1]`

---

## 2. Explanation
Inverting a tree means swapping the left and right children for **every** node in the tree.

### Approach: Recursive DFS
For a given node:
1.  Swap `left` and `right`.
2.  Recurse on `left` (which was the old right).
3.  Recurse on `right` (which was the old left).

-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

---

## 3. Pseudo Code
```text
def invertTree(root):
    if not root: return None
    
    temp = root.left
    root.left = root.right
    root.right = temp
    
    invertTree(root.left)
    invertTree(root.right)
    
    return root
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
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        if not root:
            return None
            
        # Swap children
        root.left, root.right = root.right, root.left
        
        # Recursively invert subtrees
        self.invertTree(root.left)
        self.invertTree(root.right)
        
        return root
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`[2, 1, 3]`

1.  Root `2`. Swap `1` and `3`. `[2, 3, 1]`.
2.  Recurse Left `3`. Children `null`, `null`. Swap (no-op).
3.  Recurse Right `1`. Children `null`, `null`. Swap (no-op).
4.  Return `2`.
