---
layout: page
title: "129. Sum Root to Leaf Numbers"
permalink: /courses/leetcode/prob-129-sum-root-to-leaf-numbers/
---

# 129. Sum Root to Leaf Numbers

## 1. The Question
You are given the `root` of a binary tree containing digits from `0` to `9` only.

Each root-to-leaf path in the tree represents a number.
-   For example, the root-to-leaf path `1 -> 2 -> 3` represents the number `123`.

Return the total sum of all root-to-leaf numbers. Test cases are generated so that the answer will fit in a **32-bit** integer.

### Example 1
**Input**: `root = [1,2,3]`
**Output**: `25`
**Explanation**:
Path 1->2: 12
Path 1->3: 13
Sum: 12 + 13 = 25

### Example 2
**Input**: `root = [4,9,0,5,1]`
**Output**: `1026`
**Explanation**:
Path 4->9->5: 495
Path 4->9->1: 491
Path 4->0: 40
Sum: 495 + 491 + 40 = 1026

---

## 2. Explanation
Traverse the tree DFS. Pass the `current_number` down.
`current_number = current_number * 10 + node.val`.
If leaf, return `current_number`.
If not leaf, return `sum(left) + sum(right)`.

### Approach: Recursive DFS
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

---

## 3. Pseudo Code
```text
def dfs(node, current_val):
    if not node: return 0
    current_val = current_val * 10 + node.val
    
    if not node.left and not node.right:
        return current_val
        
    return dfs(node.left, current_val) + dfs(node.right, current_val)

return dfs(root, 0)
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
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        def dfs(node, current_val):
            if not node:
                return 0
                
            current_val = current_val * 10 + node.val
            
            # Note: We must check for leaf to identify valid numbers
            # If we just returned 0 for None children, logic would be complex for nodes with 1 child.
            if not node.left and not node.right:
                return current_val
                
            return dfs(node.left, current_val) + dfs(node.right, current_val)
            
        return dfs(root, 0)
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

## 6. Example Walkthrough
`[1, 2, 3]`

1.  `dfs(1, 0)`. `val=1`.
2.  Left: `dfs(2, 1)`. `val=12`. Leaf. Return 12.
3.  Right: `dfs(3, 1)`. `val=13`. Leaf. Return 13.
4.  Total = 12 + 13 = 25.
