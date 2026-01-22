---
layout: page
title: "112. Path Sum"
permalink: /courses/leetcode/prob-112-path-sum/
---

# 112. Path Sum

## 1. The Question
Given the `root` of a binary tree and an integer `targetSum`, return `true` if the tree has a **root-to-leaf** path such that adding up all the values along the path equals `targetSum`.

A **leaf** is a node with no children.

### Example 1
**Input**: `root = [5,4,8,11,null,13,4,7,2,null,null,null,1], targetSum = 22`
**Output**: `true`
**Explanation**: Path `5 -> 4 -> 11 -> 2` sums to 22.

### Example 2
**Input**: `root = [1,2,3], targetSum = 5`
**Output**: `false`

---

## 2. Explanation
We need to traverse from root to leaf.
-   At each node, subtract `node.val` from `targetSum`.
-   If `node` is a leaf (left=None and right=None), check if `targetSum == 0`.
    -   If yes, we found a path. Return True.
-   Else, recurse left or right.

### Approach: Recursive DFS
`hasPathSum(root, sum) = hasPathSum(root.left, sum-val) OR hasPathSum(root.right, sum-val)`

-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

---

## 3. Pseudo Code
```text
def hasPathSum(root, targetSum):
    if not root: return False
    
    targetSum -= root.val
    
    # Check if leaf
    if not root.left and not root.right:
        return targetSum == 0
        
    return hasPathSum(root.left, targetSum) or hasPathSum(root.right, targetSum)
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
    def hasPathSum(self, root: Optional[TreeNode], targetSum: int) -> bool:
        if not root:
            return False
            
        targetSum -= root.val
        
        # Check if it's a leaf
        if not root.left and not root.right:
            return targetSum == 0
            
        return self.hasPathSum(root.left, targetSum) or self.hasPathSum(root.right, targetSum)
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`5 -> 4 -> 11 -> 2`, `Target=22`

1.  `Root=5`. `Need=17`.
2.  `Left=4`. `Need=13`.
3.  `Left=11`. `Need=2`.
4.  `Right=2`. `Need=0`.
    -   Leaf! `Need==0`. Return True.
Propagates True up.
