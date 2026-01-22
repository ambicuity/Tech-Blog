---
layout: page
title: "114. Flatten Binary Tree to Linked List"
permalink: /courses/leetcode/prob-114-flatten-binary-tree-to-linked-list/
---

# 114. Flatten Binary Tree to Linked List

## 1. The Question
Given the `root` of a binary tree, flatten the tree into a "linked list":
1.  The "linked list" should use the same `TreeNode` class where the `right` child pointer points to the next node in the list and the `left` child pointer is always `null`.
2.  The "linked list" should be in the same order as a **pre-order traversal** of the binary tree.

### Example 1
**Input**: `root = [1,2,5,3,4,null,6]`
**Output**: `[1,null,2,null,3,null,4,null,5,null,6]`

---

## 2. Explanation
We need `Root -> Left(flattened) -> Right(flattened)`.
Wait, preorder is `1, 2, 3, 4, 5, 6`.
So `1 -> 2 -> 3 -> 4 -> 5 -> 6`.
Basically:
1.  Flatten left subtree.
2.  Flatten right subtree.
3.  `Root.right` = `LeftFlattened`.
4.  `Root.left` = `None`.
5.  Attach `RightFlattened` to the *end* of `LeftFlattened`.

### Approach 1: Recursive Post-Order (Reverse)
If we process nodes in **Reverse Preorder** (`Right` -> `Left` -> `Root`), we can maintain a `prev` pointer (the head of the newly built list).
1.  Flatten Right.
2.  Flatten Left.
3.  `Root.right = prev`. `Root.left = None`. `prev = Root`.
This works nicely and is $O(1)$ space (recursion aside).

### Approach 2: Morris Traversal (O(1) Space)
Iterative.
For a node:
1.  If it has a left child:
2.  Find the rightmost node of the left subtree (predecessor).
3.  Connect predecessor.right to current.right.
4.  Move left child to right.
5.  Move to right (which was the left child).

We will write **Approach 1** (Recursive) as it's cleaner to explain.

---

## 3. Pseudo Code
```text
prev = None

def flatten(root):
    if not root: return
    
    flatten(root.right)
    flatten(root.left)
    
    root.right = prev
    root.left = None
    prev = root
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
    def __init__(self):
        self.prev = None
        
    def flatten(self, root: Optional[TreeNode]) -> None:
        """
        Do not return anything, modify root in-place instead.
        """
        if not root:
            return
            
        # Process in Reverse Pre-order: Right, Left, Root
        self.flatten(root.right)
        self.flatten(root.left)
        
        # Current node points to the previously processed node (which is the next in preorder)
        root.right = self.prev
        root.left = None
        self.prev = root
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$ recursion stack.

## 6. Example Walkthrough
`[1, 2, 5]`
1.  Flatten(5).
    -   Right(None). Left(None).
    -   `5.right = None`. `prev = 5`.
2.  Flatten(2).
    -   Right(None). Left(None).
    -   `2.right = 5`. `prev = 2`.
3.  Flatten(1).
    -   Flatten Right (5) - already done (Wait, recursion visits it).
    -   Flatten Left (2) - already done.
    -   `1.right = 2`. `prev = 1`.
Structure: `1 -> 2 -> 5`.
