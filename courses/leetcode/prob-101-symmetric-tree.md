---
layout: page
title: "101. Symmetric Tree"
permalink: /courses/leetcode/prob-101-symmetric-tree/
---

# 101. Symmetric Tree

## 1. The Question
Given the `root` of a binary tree, check whether it is a mirror of itself (i.e., symmetric around its center).

### Example 1
**Input**: `root = [1,2,2,3,4,4,3]`
**Output**: `true`

### Example 2
**Input**: `root = [1,2,2,null,3,null,3]`
**Output**: `false`

---

## 2. Explanation
A tree is symmetric if:
1.  Root is None (trivial).
2.  `root.left` is a mirror of `root.right`.

Two trees `t1` and `t2` are mirrors if:
1.  Both are None -> True.
2.  One is None -> False.
3.  `t1.val == t2.val` AND
4.  `t1.left` is mirror of `t2.right` AND
5.  `t1.right` is mirror of `t2.left`.

### Approach: Recursive DFS
Define a helper `isMirror(node1, node2)`.

-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

---

## 3. Pseudo Code
```text
def isSymmetric(root):
    if not root: return True
    return isMirror(root.left, root.right)

def isMirror(t1, t2):
    if not t1 and not t2: return True
    if not t1 or not t2: return False
    
    return (t1.val == t2.val) and \
           isMirror(t1.left, t2.right) and \
           isMirror(t1.right, t2.left)
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
    def isSymmetric(self, root: Optional[TreeNode]) -> bool:
        if not root:
            return True
            
        def isMirror(t1, t2):
            if not t1 and not t2:
                return True
            if not t1 or not t2:
                return False
                
            return (t1.val == t2.val) and \
                   isMirror(t1.left, t2.right) and \
                   isMirror(t1.right, t2.left)
                   
        return isMirror(root.left, root.right)
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`[1, 2, 2, 3, 4, 4, 3]`

1.  `isMirror(2(left), 2(right))`: Val matches.
    -   Check `2L(3)` vs `2R(3)`. Match.
    -   Check `2R(4)` vs `2L(4)`. Match.
2.  Returns True.
