---
layout: page
title: "98. Validate Binary Search Tree"
permalink: /courses/leetcode/prob-98-validate-binary-search-tree/
---

# 98. Validate Binary Search Tree

## 1. The Question
Given the `root` of a binary tree, determine if it is a valid binary search tree (BST).

A **valid BST** is defined as follows:
-   The left subtree of a node contains only nodes with keys **less than** the node's key.
-   The right subtree of a node contains only nodes with keys **greater than** the node's key.
-   Both the left and right subtrees must also be binary search trees.

### Example 1
**Input**: `root = [2,1,3]`
**Output**: `true`

### Example 2
**Input**: `root = [5,1,4,null,null,3,6]`
**Output**: `false`
**Explanation**: The root node's value is 5 but its right child's value is 4.

---

## 2. Explanation
A common trap is just checking `left.val < node.val` and `right.val > node.val`.
This is insufficient because all nodes in the Right Subtree must be > Root, not just the immediate child.
Example:
```
  5
 / \
1   6
   / \
  3   7
```
`3` is left child of `6` (so `< 6`), but it is in the Right subtree of `5`, so it MUST be `> 5`. But `3 < 5`, so it's invalid.

### Approach 1: Recursive with Range
Maintain a valid range `(min, max)` for each node.
-   Root range: `(-inf, +inf)`.
-   Go Left: range `(min, node.val)`.
-   Go Right: range `(node.val, max)`.
If `node.val` is not within range, return False.

### Approach 2: In-order Traversal
In-order traversal of a valid BST must be strictly increasing.
Keep track of `prev`. Check `current > prev`.

-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

---

## 3. Pseudo Code
```text
def isValidBST(root, low, high):
    if not root: return True
    
    if not (low < root.val < high):
        return False
        
    return isValidBST(root.left, low, root.val) and \
           isValidBST(root.right, root.val, high)
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
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        
        def validate(node, low, high):
            # Empty trees are valid BSTs
            if not node:
                return True
            
            # The current node's value must be between low and high
            if not (low < node.val < high):
                return False
            
            # The left subtree's nodes must be less than the current node
            # The right subtree's nodes must be greater than the current node
            return (validate(node.left, low, node.val) and 
                    validate(node.right, node.val, high))
        
        return validate(root, float('-inf'), float('inf'))
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`[5, 1, 4, null, null, 3, 6]`

1.  `Root(5)`. Range `(-inf, inf)`. OK.
2.  Left `1`: Range `(-inf, 5)`. OK.
3.  Right `4`: Range `(5, inf)`. `4 < 5` (False). Not OK.
    -   Return False.
