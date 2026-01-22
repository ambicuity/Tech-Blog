---
layout: page
title: "199. Binary Tree Right Side View"
permalink: /courses/leetcode/prob-199-binary-tree-right-side-view/
---

# 199. Binary Tree Right Side View

## 1. The Question
Given the `root` of a binary tree, imagine yourself standing on the **right side** of it, return the values of the nodes you can see ordered from top to bottom.

### Example 1
**Input**: `root = [1,2,3,null,5,null,4]`
**Output**: `[1,3,4]`

### Example 2
**Input**: `root = [1,null,3]`
**Output**: `[1,3]`

### Example 3
**Input**: `root = []`
**Output**: `[]`

---

## 2. Explanation
We need to capture the **last node** of every level.

### Approach 1: BFS
Traverse level by level.
For each level, the last element popped (or accessed) is the rightmost element.

### Approach 2: DFS (Right First)
Traverse `Root -> Right -> Left`.
Keep track of current `depth`.
If `depth == len(result)`, it means we haven't visited this depth yet (since we go Right first, the first node we see at a new depth is the Rightmost). Add it to result.

-   **Time**: $O(N)$.
-   **Space**: $O(H)$.

We will use **BFS** as it is the standard for "Level" problems.

---

## 3. Pseudo Code
```text
if not root: return []
queue = [root]
res = []

while queue:
    level_size = len(queue)
    for i in range(level_size):
        node = queue.pop(0)
        if i == level_size - 1:
            res.append(node.val)
        
        if node.left: queue.append(node.left)
        if node.right: queue.append(node.right)

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
    def rightSideView(self, root: Optional[TreeNode]) -> list[int]:
        if not root:
            return []
            
        result = []
        queue = [root]
        
        while queue:
            level_length = len(queue)
            
            for i in range(level_length):
                node = queue.pop(0)
                
                # If it's the last node in the current level, add to result
                if i == level_length - 1:
                    result.append(node.val)
                    
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
                    
        return result
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(W)$ (max width of tree) or $O(N)$ for leaf level.

## 6. Example Walkthrough
`[1, 2, 3, null, 5, null, 4]`

1.  Q: `[1]`. Size=1.
    -   Pop 1. Last? Yes. Res: `[1]`.
    -   Push 2, 3. Q: `[2, 3]`.
2.  Q: `[2, 3]`. Size=2.
    -   Pop 2. Last? No. Push 5. Q: `[3, 5]`.
    -   Pop 3. Last? Yes. Res: `[1, 3]`. Push 4. Q: `[5, 4]`.
3.  Q: `[5, 4]`. Size=2.
    -   Pop 5. Last? No.
    -   Pop 4. Last? Yes. Res: `[1, 3, 4]`.
Done.
