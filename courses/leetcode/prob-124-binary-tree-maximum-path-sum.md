---
layout: page
title: "124. Binary Tree Maximum Path Sum"
permalink: /courses/leetcode/prob-124-binary-tree-maximum-path-sum/
---

# 124. Binary Tree Maximum Path Sum

## 1. The Question
A **path** in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them. A node can only appear in the sequence **at most once**. Note that the path does not need to pass through the root.

The **path sum** of a path is the sum of the node's values in the path.

Given the `root` of a binary tree, return the maximum **path sum** of any **non-empty** path.

### Example 1
**Input**: `root = [1,2,3]`
**Output**: `6`
**Explanation**: The optimal path is 2 -> 1 -> 3 with a path sum of 2 + 1 + 3 = 6.

### Example 2
**Input**: `root = [-10,9,20,15,7]`
**Output**: `42`
**Explanation**: The optimal path is 15 -> 20 -> 7 with a path sum of 15 + 20 + 7 = 42.

---

## 2. Explanation
For any node `u`, the max path passing through `u` (as the highest node in the path) is:
`u.val + max(left_gain, 0) + max(right_gain, 0)`.
Where `left_gain` is the max path sum starting from `u.left` going downwards.
The recursion function should return `u.val + max(left_gain, right_gain, 0)` to its parent (contribution to parent).
We maintain a global maximum.

-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

---

## 3. Pseudo Code
```text
max_sum = -inf
def gain(node):
    if not node: return 0
    left = max(gain(node.left), 0)
    right = max(gain(node.right), 0)
    
    current_path = node.val + left + right
    max_sum = max(max_sum, current_path)
    
    return node.val + max(left, right)

gain(root)
return max_sum
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
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        self.max_sum = float('-inf')
        
        def max_gain(node):
            if not node:
                return 0
            
            # Max sum from left child (ignore if negative)
            left_gain = max(max_gain(node.left), 0)
            
            # Max sum from right child (ignore if negative)
            right_gain = max(max_gain(node.right), 0)
            
            # Price to start a new path where `node` is highest point
            price_newpath = node.val + left_gain + right_gain
            
            # Update global max
            self.max_sum = max(self.max_sum, price_newpath)
            
            # Return max gain the node and one of its subtrees to the parent
            return node.val + max(left_gain, right_gain)
            
        max_gain(root)
        return self.max_sum
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`[-10, 9, 20, 15, 7]`
1.  Leaves 15, 7, 9 return values `15, 7, 9`.
2.  `20`. Left `15`, Right `7`.
    -   New Path: `20 + 15 + 7 = 42`. Max=42.
    -   Returns `20 + 15 = 35`.
3.  `-10`. Left `9`, Right `35`.
    -   New Path: `-10 + 9 + 35 = 34`. Max=42.
    -   Returns `-10 + 35 = 25`.
Result 42.
