---
layout: page
title: "230. Kth Smallest Element in a BST"
permalink: /courses/leetcode/prob-230-kth-smallest-element-in-a-bst/
---

# 230. Kth Smallest Element in a BST

## 1. The Question
Given the `root` of a binary search tree, and an integer `k`, return the `k`th smallest value (1-indexed) of all the values of the nodes in the tree.

### Example 1
**Input**: `root = [3,1,4,null,2], k = 1`
**Output**: `1`

### Example 2
**Input**: `root = [5,3,6,2,4,null,null,1], k = 3`
**Output**: `3`

---

## 2. Explanation
In a BST, In-order traversal gives sorted values.
We just need to find the `k`-th element visited in In-order traversal.

-   **Time**: $O(H + k)$. We traverse down to the smallest element ($H$) and then traverse $k$ nodes.
-   **Space**: $O(H)$ for recursion or stack.

### Approach 1: Recursive Inorder
Count `k` down.
1.  Recurse Left.
2.  Decrement `k`.
3.  If `k == 0`, return current node val.
4.  Recurse Right.

---

## 3. Pseudo Code
```text
count = k
res = None

def inorder(node):
    if not node or res: return
    
    inorder(node.left)
    
    count -= 1
    if count == 0:
        res = node.val
        return
        
    inorder(node.right)
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
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        self.k = k
        self.result = 0
        
        def inorder(node):
            if not node:
                return
            
            inorder(node.left)
            
            self.k -= 1
            if self.k == 0:
                self.result = node.val
                return
            
            # Optimization: If result found found, stop traversing
            if self.k > 0:
                inorder(node.right)
                
        inorder(root)
        return self.result
```

---

## 5. Complexity
-   **Time**: $O(H+k)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`[3, 1, 4, null, 2]`, `k=1`
`Inorder`: 1, 2, 3, 4.

1.  Left to 1.
2.  Process 1. `k` becomes 0. Result=1.
3.  Return 1.
