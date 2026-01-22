---
layout: page
title: "108. Convert Sorted Array to Binary Search Tree"
permalink: /courses/leetcode/prob-108-convert-sorted-array-to-binary-search-tree/
---

# 108. Convert Sorted Array to Binary Search Tree

## 1. The Question
Given an integer array `nums` where the elements are sorted in **ascending order**, convert it to a **height-balanced** binary search tree.

A **height-balanced** binary tree is a binary tree in which the depth of the two subtrees of every node never differs by more than one.

### Example 1
**Input**: `nums = [-10,-3,0,5,9]`
**Output**: `[0,-3,9,-10,null,5]`
**Explanation**: `[0,-10,5,null,-3,null,9]` is also accepted.

---

## 2. Explanation
To build a **balanced** BST from a sorted array:
1.  The middle element of the array must be the root.
2.  The left half of the array becomes the left subtree.
3.  The right half of the array becomes the right subtree.
This ensures equal number of nodes (approx) on both sides, minimizing height.

-   **Time**: $O(N)$.
-   **Space**: $O(\log N)$ (recursion stack).

---

## 3. Pseudo Code
```text
def sortedArrayToBST(nums):
    if not nums: return None
    
    mid = len(nums) // 2
    root = TreeNode(nums[mid])
    
    root.left = sortedArrayToBST(nums[:mid])
    root.right = sortedArrayToBST(nums[mid+1:])
    
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
    def sortedArrayToBST(self, nums: list[int]) -> Optional[TreeNode]:
        def helper(left, right):
            if left > right:
                return None
            
            # Choose middle element as root
            mid = (left + right) // 2
            
            # Preorder traversal: Node -> Left -> Right
            root = TreeNode(nums[mid])
            root.left = helper(left, mid - 1)
            root.right = helper(mid + 1, right)
            
            return root
            
        return helper(0, len(nums) - 1)
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(\log N)$.

## 6. Example Walkthrough
`[-10, -3, 0, 5, 9]`

1.  Mid index 2. Val `0`. Root `0`.
2.  Left `[-10, -3]`. Mid index 0 (or 1). Say `-10` or `-3`.
    -   If `-3` (index 1 of sub), Left child is `0.left`.
    -   `helper(0, 1)`. Mid 0 (`-10`).
    -   `root` is `-10`. Left `helper(0, -1)` (None). Right `helper(1, 1)` -> `-3`.
    -   So `0.left` is `-10`, which has right child `-3`.
(Or simple `[-3]` root, left child `-10`).
3.  Right `[5, 9]`. Root `9`. Left `5`.
Structure: `0 -> (-3 (Left: -10), 9 (Left: 5))`.
Valid Balanced BST.
