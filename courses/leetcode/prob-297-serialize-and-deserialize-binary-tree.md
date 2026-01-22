---
layout: page
title: "297. Serialize and Deserialize Binary Tree"
permalink: /courses/leetcode/prob-297-serialize-and-deserialize-binary-tree/
---

# 297. Serialize and Deserialize Binary Tree

## 1. The Question
Serialization is the process of converting a data structure or object into a sequence of bits so that it can be stored in a file or memory buffer, or transmitted across a network connection link to be reconstructed later in the same or another computer environment.

Design an algorithm to serialize and deserialize a binary tree. There is no restriction on how your serialization/deserialization algorithm should work. You just need to ensure that a binary tree can be serialized to a string and this string can be deserialized to the original tree structure.

### Example 1
**Input**: `root = [1,2,3,null,null,4,5]`
**Output**: `[1,2,3,null,null,4,5]`

---

## 2. Explanation
We can use **Preorder Traversal** (DFS) or **Level Order Traversal** (BFS).
Let's use DFS (Preorder) as it's often more intuitive for reconstruction.
Serialization:
-   If node is null, append "N".
-   If node exists, append "val", then recurse left, then right.
-   Delimiter `,`.

Deserialization:
-   Split string by `,`. Use an iterator/queue.
-   Pop first token.
-   If "N", return None.
-   Create node with value.
-   `node.left = recurse()`.
-   `node.right = recurse()`.
-   Return node.

-   **Time**: $O(N)$. Each node visited once.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
def serialize(root):
    if not root: return "N"
    return str(root.val) + "," + serialize(root.left) + "," + serialize(root.right)

def deserialize(data):
    vals = iter(data.split(","))
    def build():
        v = next(vals)
        if v == "N": return None
        node = TreeNode(int(v))
        node.left = build()
        node.right = build()
        return node
    return build()
```

---

## 4. Optimal Code (Python)

```python
# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Codec:

    def serialize(self, root):
        """Encodes a tree to a single string.
        
        :type root: TreeNode
        :rtype: str
        """
        vals = []
        def dfs(node):
            if not node:
                vals.append("N")
            else:
                vals.append(str(node.val))
                dfs(node.left)
                dfs(node.right)
        dfs(root)
        return ",".join(vals)
        

    def deserialize(self, data):
        """Decodes your encoded data to tree.
        
        :type data: str
        :rtype: TreeNode
        """
        vals =  iter(data.split(","))
        
        def dfs():
            val = next(vals)
            if val == "N":
                return None
            
            node = TreeNode(int(val))
            node.left = dfs()
            node.right = dfs()
            return node
            
        return dfs()
        

# Your Codec object will be instantiated and called as such:
# ser = Codec()
# deser = Codec()
# ans = deser.deserialize(ser.serialize(root))
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`[1, 2, 3]`.
Ser: `1,2,N,N,3,N,N`.
Deser:
1.  Pop `1`. Root.
2.  Left Recurse. Pop `2`. Node 2.
    -   Left Recurse. Pop `N`. Return None.
    -   Right Recurse. Pop `N`. Return None.
    -   `2.left=None, 2.right=None`. Return 2.
3.  Right Recurse. Pop `3`. Node 3.
    -   Left `N`. Right `N`.
4.  Return 1.
Tree restored.
