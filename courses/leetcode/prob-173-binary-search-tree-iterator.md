---
layout: page
title: "173. Binary Search Tree Iterator"
permalink: /courses/leetcode/prob-173-binary-search-tree-iterator/
---

# 173. Binary Search Tree Iterator

## 1. The Question
Implement the `BSTIterator` class that represents an iterator over the **in-order traversal** of a binary search tree (BST):
-   `BSTIterator(TreeNode root)` Initializes an object of the `BSTIterator` class. The root of the BST is given as part of the constructor. The pointer should be initialized to a non-existent number smaller than any element in the BST.
-   `boolean hasNext()` Returns `true` if there is a number in the traversal to the right of the pointer, otherwise returns `false`.
-   `int next()` Moves the pointer to the right, then returns the number at the pointer.

Notice that by initializing the pointer to a non-existent smallest number, the first call to `next()` will return the smallest element in the BST.

You may assume that `next()` calls will always be valid. That is, there will be at least a next number in the in-order traversal when `next()` is called.

**Constraints:**
-   `next()` and `hasNext()` should run in average `O(1)` time and use `O(h)` memory, where `h` is the height of the tree.

### Example 1
**Input**
`["BSTIterator", "next", "next", "hasNext", "next", "hasNext", "next", "hasNext", "next", "hasNext"]`
`[[[7, 3, 15, null, null, 9, 20]], [], [], [], [], [], [], [], [], []]`
**Output**
`[null, 3, 7, true, 9, true, 15, true, 20, false]`

---

## 2. Explanation
To iterate Inorder (`Left`, `Root`, `Right`) step-by-step:
1.  Go as Left as possible, pushing nodes to a Stack.
2.  `next()`:
    -   Pop from stack. This is the current smallest (Top).
    -   If the popped node has a Right child, go to Right, then go as Left as possible from there (pushing to stack).
    -   Return popped value.
3.  `hasNext()`: Checked if stack is empty.

This simulates the recursive stack of an Inorder DFS.

-   **Time**: $O(1)$ amortized. Each node is pushed and popped exactly once.
-   **Space**: $O(H)$. Stack stores left spine.

---

## 3. Pseudo Code
```text
class BSTIterator:
    stack = []
    
    _push_left(node):
        while node:
            stack.push(node)
            node = node.left

    init(root):
        _push_left(root)
        
    next():
        node = stack.pop()
        _push_left(node.right)
        return node.val
        
    hasNext():
        return not stack.empty()
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

class BSTIterator:

    def __init__(self, root: Optional[TreeNode]):
        self.stack = []
        self._push_left(root)

    def _push_left(self, node):
        """Push all left children of the node onto the stack."""
        while node:
            self.stack.append(node)
            node = node.left

    def next(self) -> int:
        """
        Returns the next smallest number
        """
        # Node at top of stack is the next in in-order
        node = self.stack.pop()
        
        # If this node has a right child, we need to process its left subtree
        if node.right:
            self._push_left(node.right)
            
        return node.val

    def hasNext(self) -> bool:
        return len(self.stack) > 0
```

---

## 5. Complexity
-   **Time**: $O(1)$ amortized.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`[7, 3, 15]`
1.  Init: Push 7, Push 3. Stack: `[7, 3]`.
2.  Next: Pop 3. `3.right` is null. Stack: `[7]`. Return 3.
3.  Next: Pop 7. `7.right` is 15. Push 15. Stack: `[15]`. Return 7.
4.  Next: Pop 15. ... Return 15.
