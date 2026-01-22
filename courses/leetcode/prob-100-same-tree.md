---
layout: page
title: "100. Same Tree"
permalink: /courses/leetcode/prob-100-same-tree/
---

# 100. Same Tree

## 1. The Question
Given the roots of two binary trees `p` and `q`, write a function to check if they are the same or not.

Two binary trees are considered the same if they are structurally identical, and the nodes have the same value.

### Example 1
**Input**: `p = [1,2,3], q = [1,2,3]`
**Output**: `true`

### Example 2
**Input**: `p = [1,2], q = [1,null,2]`
**Output**: `false`

---

## 2. Explanation
We need to verify three things for every corresponding node:
1.  Are both `None`? -> Yes (Base Case True).
2.  Is one `None` and the other not? -> No (False).
3.  Do they have the same value?
    -   If yes, recurse on left children AND right children.

### Approach: Recursive DFS
`isSame(p, q) = (p.val == q.val) AND isSame(p.left, q.left) AND isSame(p.right, q.right)`

-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

---

## 3. Pseudo Code
```text
def isSameTree(p, q):
    if not p and not q: return True
    if not p or not q: return False
    if p.val != q.val: return False
    
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)
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
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        # Both empty
        if not p and not q:
            return True
            
        # One empty or values different
        if not p or not q or p.val != q.val:
            return False
            
        # Recurse
        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`p=[1,2], q=[1,null,2]`

1.  `1` vs `1`. Match. Recurse left.
2.  `2` vs `null`. Mismatch. Return False.
3.  Propagate element False up. Return False.
