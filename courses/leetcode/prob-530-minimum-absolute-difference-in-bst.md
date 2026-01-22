---
layout: page
title: "530. Minimum Absolute Difference in BST"
permalink: /courses/leetcode/prob-530-minimum-absolute-difference-in-bst/
---

# 530. Minimum Absolute Difference in BST

## 1. The Question
Given the `root` of a Binary Search Tree (BST), return the minimum absolute difference between the values of any two different nodes in the tree.

### Example 1
**Input**: `root = [4,2,6,1,3]`
**Output**: `1`

### Example 2
**Input**: `root = [1,0,48,null,null,12,49]`
**Output**: `1`

---

## 2. Explanation
In a BST, In-order traversal yields sorted values.
The minimum difference must occur between **adjacent** values in the sorted sequence.
So, we can perform an In-order traversal and compare `current_val - prev_val`.

-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

---

## 3. Pseudo Code
```text
min_diff = infinity
prev = None

def inorder(node):
    if not node: return
    
    inorder(node.left)
    
    if prev is not None:
        min_diff = min(min_diff, node.val - prev.val)
    prev = node
    
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
    def getMinimumDifference(self, root: Optional[TreeNode]) -> int:
        self.min_diff = float('inf')
        self.prev = None
        
        def inorder(node):
            if not node:
                return
            
            inorder(node.left)
            
            if self.prev is not None:
                self.min_diff = min(self.min_diff, node.val - self.prev.val)
            self.prev = node
            
            inorder(node.right)
            
        inorder(root)
        return self.min_diff
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`[4, 2, 6, 1, 3]`
Inorder: `1, 2, 3, 4, 6`.

1.  `1`. Prev=None. Prev=1.
2.  `2`. Diff `2-1=1`. Min=1. Prev=2.
3.  `3`. Diff `3-2=1`. Min=1. Prev=3.
4.  `4`. Diff `4-3=1`. Min=1. Prev=4.
5.  `6`. Diff `6-4=2`. Min=1. Prev=6.

Result: 1.
