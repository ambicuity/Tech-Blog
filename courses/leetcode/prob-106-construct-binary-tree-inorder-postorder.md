---
layout: page
title: "106. Construct Binary Tree from Inorder and Postorder Traversal"
permalink: /courses/leetcode/prob-106-construct-binary-tree-inorder-postorder/
---

# 106. Construct Binary Tree from Inorder and Postorder Traversal

## 1. The Question
Given two integer arrays `inorder` and `postorder` where `inorder` is the inorder traversal of a binary tree and `postorder` is the postorder traversal of the same tree, construct and return the binary tree.

### Example 1
**Input**: `inorder = [9,3,15,20,7], postorder = [9,15,7,20,3]`
**Output**: `[3,9,20,null,null,15,7]`

### Example 2
**Input**: `inorder = [-1], postorder = [-1]`
**Output**: `[-1]`

---

## 2. Explanation
-   **Inorder**: Left, Root, Right.
-   **Postorder**: Left, Right, Root.

1.  The **last** element of `postorder` is ALWAYS the **Root**.
2.  Find Root in `inorder`. Split into Left/Right subtrees.
3.  Recursively build.
    -   **Important**: Since we are popping from the end of `postorder`, we encounter Root, then **Right**, then **Left**. So we should build the recursive calls in that order if we use a global index, or carefully calculate ranges.

### Approach: Hash Map + Recursion
Similar to Q105. Use a map for `inorder` lookups.

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
map = {val: idx for idx, val in enumerate(inorder)}

def build(in_start, in_end, post_start, post_end):
    if in_start > in_end: return None
    
    val = postorder[post_end] # Root is at end of postorder
    root = TreeNode(val)
    idx = map[val]
    
    right_size = in_end - idx
    
    # Left Subtree:
    # In: [in_start : idx-1]
    # Post: [post_start : post_end - right_size - 1]
    
    # Right Subtree:
    # In: [idx+1 : in_end]
    # Post: [post_end - right_size : post_end - 1]
    
    root.left = build(in_start, idx-1, post_start, post_end-right_size-1)
    root.right = build(idx+1, in_end, post_end-right_size, post_end-1)
    
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
    def buildTree(self, inorder: list[int], postorder: list[int]) -> Optional[TreeNode]:
        inorder_map = {val: idx for idx, val in enumerate(inorder)}
        
        def helper(in_left, in_right, post_left, post_right):
            if in_left > in_right:
                return None
                
            # The last element in post_order is the root
            root_val = postorder[post_right]
            root = TreeNode(root_val)
            
            root_idx = inorder_map[root_val]
            
            # Calculate size of right subtree (elements to right of root in inorder)
            right_subtree_size = in_right - root_idx
            
            # Recursively build
            # Right Child:
            # Inorder: [root_idx + 1 : in_right]
            # Postorder: [post_right - right_size : post_right - 1]
            root.right = helper(root_idx + 1, in_right, 
                                post_right - right_subtree_size, post_right - 1)
                                
            # Left Child:
            # Inorder: [in_left : root_idx - 1]
            # Postorder: [post_left : post_right - right_size - 1]
            root.left = helper(in_left, root_idx - 1, 
                               post_left, post_right - right_subtree_size - 1)
                               
            return root
            
        return helper(0, len(inorder) - 1, 0, len(postorder) - 1)
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`In: [9,3,15,20,7]`, `Post: [9,15,7,20,3]`

1.  `Root = 3`. Index 1. `RightSize = 3`.
2.  `Right`: In `[15,20,7]`. Post `[15,7,20]`. Root `20`.
    -   Left `15`. Right `7`.
3.  `Left`: In `[9]`. Post `[9]`. Root `9`.
4.  Tree: `3 -> (9, 20(15, 7))`.
