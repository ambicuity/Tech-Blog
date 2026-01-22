---
layout: page
title: "637. Average of Levels in Binary Tree"
permalink: /courses/leetcode/prob-637-average-of-levels-in-binary-tree/
---

# 637. Average of Levels in Binary Tree

## 1. The Question
Given the `root` of a binary tree, return the average value of the nodes on each level in the form of an array. Answers within `10^-5` of the actual answer will be accepted.

### Example 1
**Input**: `root = [3,9,20,null,null,15,7]`
**Output**: `[3.00000,14.50000,11.00000]`
**Explanation**: The average value of nodes on level 0 is 3, on level 1 is 14.5, and on level 2 is 11.
Hence return [3, 14.5, 11].

---

## 2. Explanation
Standard BFS. for each level, calculate sum and divide by count.

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
if not root: return []
q = [root]
res = []

while q:
    cnt = len(q)
    level_sum = 0
    for i in range(cnt):
        node = q.pop(0)
        level_sum += node.val
        if node.left: q.append(node.left)
        if node.right: q.append(node.right)
    
    res.append(level_sum / cnt)

return res
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
    def averageOfLevels(self, root: Optional[TreeNode]) -> list[float]:
        if not root:
            return []
            
        result = []
        queue = [root]
        
        while queue:
            level_len = len(queue)
            level_sum = 0
            
            for _ in range(level_len):
                node = queue.pop(0)
                level_sum += node.val
                
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
                    
            result.append(level_sum / level_len)
            
        return result
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`[3, 9, 20]`

1.  Level 0: `[3]`. Sum=3, Cnt=1. Avg=3.0.
2.  Level 1: `[9, 20]`. Sum=29, Cnt=2. Avg=14.5.
