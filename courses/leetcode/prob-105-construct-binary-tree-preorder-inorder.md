---
layout: page
title: "105. Construct Binary Tree from Preorder and Inorder Traversal"
permalink: /courses/leetcode/prob-105-construct-binary-tree-preorder-inorder/
---

# 105. Construct Binary Tree from Preorder and Inorder Traversal

## 1. The Question
Given two integer arrays `preorder` and `inorder` where `preorder` is the preorder traversal of a binary tree and `inorder` is the inorder traversal of the same tree, construct and return the binary tree.

### Example 1
**Input**: `preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]`
**Output**: `[3,9,20,null,null,15,7]`

### Example 2
**Input**: `preorder = [-1], inorder = [-1]`
**Output**: `[-1]`

---

## 2. Explanation
-   **Preorder**: Root, Left, Right.
-   **Inorder**: Left, Root, Right.

1.  The first element of `preorder` is ALWAYS the **Root**.
2.  Find the Root in `inorder`. All elements to the left are in the **Left Subtree**. All elements to the right are in the **Right Subtree**.
3.  Recursively build left and right subtrees.

Example: `Pre: [3, 9, 20, 15, 7]`, `In: [9, 3, 15, 20, 7]`
1.  Root = 3.
2.  In `In`, `9` is left of `3`, `15, 20, 7` are right.
3.  Left size = 1.
4.  Recursive split `Pre` and `In` arrays.

-   **Time**: $O(N^2)$ with slicing or $O(N)$ with hash map.
-   **Space**: $O(N)$ for map + recursion.

### Approach: Hash Map for Fast Indexing
Finding the root in `inorder` takes $O(N)$. We can optimize this by building a map `value -> index` for `inorder` first.

---

## 3. Pseudo Code
```text
map = {val: idx for idx, val in enumerate(inorder)}

def build(pre_start, pre_end, in_start, in_end):
    if pre_start > pre_end: return None
    
    val = preorder[pre_start]
    root = TreeNode(val)
    idx = map[val]
    
    left_size = idx - in_start
    
    root.left = build(pre_start+1, pre_start+left_size, in_start, idx-1)
    root.right = build(pre_start+left_size+1, pre_end, idx+1, in_end)
    
    return root

return build(0, n-1, 0, n-1)
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
    def buildTree(self, preorder: list[int], inorder: list[int]) -> Optional[TreeNode]:
        # Map inorder values to their indices for O(1) lookup
        inorder_map = {val: idx for idx, val in enumerate(inorder)}
        
        def helper(pre_left, pre_right, in_left, in_right):
            if pre_left > pre_right:
                return None
                
            # The first node in preorder is the root
            root_val = preorder[pre_left]
            root = TreeNode(root_val)
            
            # Find root position in inorder
            root_idx = inorder_map[root_val]
            
            # Count nodes in left subtree
            left_subtree_size = root_idx - in_left
            
            # Recursively build left and right subtrees
            # Left Subtree:
            # Preorder: [pre_left+1 : pre_left+left_size]
            # Inorder: [in_left : root_idx-1]
            root.left = helper(pre_left + 1, pre_left + left_subtree_size,
                               in_left, root_idx - 1)
                               
            # Right Subtree:
            # Preorder: [pre_left+left_size+1 : pre_right]
            # Inorder: [root_idx+1 : in_right]
            root.right = helper(pre_left + left_subtree_size + 1, pre_right,
                                root_idx + 1, in_right)
                                
            return root
            
        return helper(0, len(preorder) - 1, 0, len(inorder) - 1)
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`Pre: [3, 9, 20, 15, 7]`, `In: [9, 3, 15, 20, 7]`

1.  `Root=3`. `idx=1`. `LeftSize=1`.
2.  Left: `helper(Pre: 1~1, In: 0~0)`. `9`.
    -   `Root=9`. `idx=0`. `LeftSize=0`.
    -   Left: `helper(2,1...)` -> `None`.
    -   Right: `helper(2,1...)` -> `None`.
    -   Returns `9`.
3.  Right: `helper(Pre: 2~4, In: 2~4)`. `20`.
    -   `Root=20`. `idx=3`. `LeftSize=1` (15).
    -   Left: `15`.
    -   Right: `7`.
    -   Returns `20`.
4.  Returns `3 -> (9, 20)`.
