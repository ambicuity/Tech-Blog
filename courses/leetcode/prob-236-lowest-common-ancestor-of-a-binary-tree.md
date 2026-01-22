---
layout: page
title: "236. Lowest Common Ancestor of a Binary Tree"
permalink: /courses/leetcode/prob-236-lowest-common-ancestor-of-a-binary-tree/
---

# 236. Lowest Common Ancestor of a Binary Tree

## 1. The Question
Given a binary tree, find the lowest common ancestor (LCA) of two given nodes in the tree.

According to the definition of LCA on Wikipedia: “The lowest common ancestor is defined between two nodes `p` and `q` as the lowest node in `T` that has both `p` and `q` as descendants (where we allow a node to be a descendant of itself).”

### Example 1
**Input**: `root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1`
**Output**: `3`
**Explanation**: The LCA of nodes 5 and 1 is 3.

### Example 2
**Input**: `root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 4`
**Output**: `5`
**Explanation**: The LCA of nodes 5 and 4 is 5, since a node can be a descendant of itself according to the LCA definition.

---

## 2. Explanation
We need to find the node where the paths to `p` and `q` diverge.
In a recursive traversal:
1.  If current node is `p` or `q`, return current node.
2.  Search Left.
3.  Search Right.
4.  If both Left and Right returned non-null, it means `p` is in one branch and `q` is in the other. **Current node is LCA**.
5.  If only one returned non-null, propagate that one up (LCA is higher up or already found).

-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

---

## 3. Pseudo Code
```text
def lca(root, p, q):
    if not root: return None
    if root == p or root == q: return root
    
    left = lca(root.left, p, q)
    right = lca(root.right, p, q)
    
    if left and right:
        return root
        
    return left if left else right
```

---

## 4. Optimal Code (Python)

```python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        if not root:
            return None
            
        # If either p or q is the root, then the root is the LCA 
        # (or the ancestor of the LCA, which effectively bubbles up)
        if root == p or root == q:
            return root
            
        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)
        
        # If both left and right returned a node, it means p and q are found in 
        # different subtrees of the current node. Thus, current node is the LCA.
        if left and right:
            return root
            
        # Otherwise, return the non-null child (bubbling up the found node)
        return left if left else right
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`Root=3, p=5, q=4` (4 is child of 5).

1.  `LCA(3)`.
    -   Left: `LCA(5)`.
        -   `Root == p`. Return `5`.
    -   Right: `LCA(1)`.
        -   Search children... not found. Return `None` (assuming 4 not there).
    -   Result: `left=5, right=None`. Return `5`.
Correct.
