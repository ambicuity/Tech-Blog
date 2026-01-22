---
layout: page
title: "222. Count Complete Tree Nodes"
permalink: /courses/leetcode/prob-222-count-complete-tree-nodes/
---

# 222. Count Complete Tree Nodes

## 1. The Question
Given the `root` of a **complete** binary tree, return the number of the nodes.

According to Wikipedia, every level, except possibly the last, is completely filled in a complete binary tree, and all nodes in the last level are as far left as possible. It can have between `1` and `2^h` nodes inclusive at the last level `h`.

Design an algorithm that runs in less than `O(n)` time complexity.

### Example 1
**Input**: `root = [1,2,3,4,5,6]`
**Output**: `6`

### Example 2
**Input**: `root = []`
**Output**: `0`

---

## 2. Explanation
A naive `count` takes $O(N)$. We need better.
We can use the property of Complete Binary Tree.
1.  Check depth of Leftmost path (`d_left`) and Rightmost path (`d_right`).
2.  If `d_left == d_right`, it is a **Perfect Binary Tree**.
    -   Nodes = $2^{d\_left} - 1$.
3.  If not, recursively count `1 + count(left) + count(right)`.

Since at least one subtree will always be perfect at each step, we save time.
-   **Time**: $O(\log^2 N)$. (Height is $\log N$, and we calculate height ($\log N$) at each step).

### Approach 2: Binary Search on Leaf Nodes
We know how many details are in full levels ($2^H - 1$). We just need to find how many leaves are in the last level.
We can binary search the existence of the $k$-th leaf.
-   **Time**: $O(\log^2 N)$.

We will use **Approach 1** (Recursive Height Check) as it's easier to implement.

---

## 3. Pseudo Code
```text
def countNodes(root):
    if not root: return 0
    
    h_left = depth(root.left)
    h_right = depth(root.right)
    
    if h_left == h_right:
        # Left subtree is perfect.
        # Nodes = Root (1) + Left (2^h_l - 1) + Count(Right)
        # = 2^h_l + countNodes(root.right)
        pass 
        
    # Wait, simple recursion with height check:
    hl = 0, node = root
    while node: hl++, node = node.left
    
    hr = 0, node = root
    while node: hr++, node = node.right
    
    if hl == hr: return 2^hl - 1
    return 1 + countNodes(left) + countNodes(right)
```

Correction on Logic:
Actually, `get_height` only goes left.
We compare height of left subtree and height of right subtree.
-   If `height(right) == height(left)`, then left subtree is perfect full.
    -   Left nodes = $2^h - 1$.
    -   Total = $(2^h - 1) + 1 (root) + count(right) = 2^h + count(right)$.
-   If `height(right) < height(left)`, then right subtree is perfect (but one level shorter).
    -   Right nodes = $2^{h-1} - 1$.
    -   Total = $(2^{h-1} - 1) + 1 (root) + count(left) = 2^{h-1} + count(left)$.

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
    def countNodes(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
            
        left_depth = self.get_depth(root.left)
        right_depth = self.get_depth(root.right)
        
        if left_depth == right_depth:
            # Left subtree is a perfect binary tree of height left_depth
            # It has 2^left_depth - 1 nodes.
            # Plus root (1), total is 2^left_depth.
            # We add nodes from the right subtree recursively.
            return (1 << left_depth) + self.countNodes(root.right)
        else:
            # Right subtree is a perfect binary tree of height right_depth (which is left_depth - 1)
            # It has 2^right_depth - 1 nodes.
            # Plus root (1), total is 2^right_depth.
            # We add nodes from the left subtree recursively.
            return (1 << right_depth) + self.countNodes(root.left)
            
    def get_depth(self, node):
        depth = 0
        while node:
            depth += 1
            node = node.left
        return depth
```

---

## 5. Complexity
-   **Time**: $O(\log^2 N)$.
-   **Space**: $O(\log N)$.

## 6. Example Walkthrough
`[1, 2, 3, 4, 5, 6]` (Depth 2).

1.  `Root(1)`. LeftDepth=2 (4->2). RightDepth=1 (6->3). `2 != 1`.
    -   Right is perfect height 1. `2^1 + count(left)`.
    -   `2 + count(2)`.
2.  `Count(2)`. LeftDepth=1 (4). RightDepth=1 (5). Equal.
    -   Left is perfect height 1. `2^1 + count(right)`.
    -   `2 + count(5)`.
3.  `Count(5)`. Leaf. L=0, R=0.
    -   `1 + count(None) = 1`.
Total: `2 + 2 + 1 + 0 = 5`.
Wait, input `[1,2,3,4,5,6]` has 6 nodes.
Let's retrace logic:
`left_depth` of Root is 2 (Logic: `root.left` -> `2` -> `4`. Depth 2).
`right_depth` of Root is 2 (Logic: `root.right` -> `3` -> `6`. Depth 2).
Wait, `get_depth` goes LEFT only.
Root(1).
`get_depth(2)` -> 2 -> 4 (Depth 2).
`get_depth(3)` -> 3 -> 6 (Depth 2).
Equal.
Result: `2^2 + count(3)`. `4 + count(3)`.

`count(3)`: `get_depth(6)`->1. `get_depth(null)`->0.
Not Equal.
Result: `2^0 + count(6)`. `1 + count(6)`.

`count(6)`: Leaf. Returns 1.

Total: `4 + 1 + 1 = 6`. Correct.
