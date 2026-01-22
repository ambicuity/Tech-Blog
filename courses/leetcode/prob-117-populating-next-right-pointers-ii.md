---
layout: page
title: "117. Populating Next Right Pointers in Each Node II"
permalink: /courses/leetcode/prob-117-populating-next-right-pointers-ii/
---

# 117. Populating Next Right Pointers in Each Node II

## 1. The Question
Given a binary tree, populate each next pointer to point to its next right node. If there is no next right node, the next pointer should be set to `NULL`.

Initially, all next pointers are set to `NULL`.

Look at the example: Flattening levels. This is a generic tree (not necessarily perfect).

### Example 1
**Input**: `root = [1,2,3,4,5,null,7]`
**Output**: `[1,#,2,3,#,4,5,7,#]`
**Explanation**:
Level 0: 1->#
Level 1: 2->3->#
Level 2: 4->5->7->#

---

## 2. Explanation
We need to connect nodes at the same level.
Standard BFS using a Queue takes $O(N)$ space.
Can we do it in $O(1)$ space?

### Approach: Level-Order Traversal using Next Pointers
Since steps `i` build the next pointers for level `i+1`, we can use the `next` pointers of the *current* level to traverse it, while building the linked list for the *next* level.

We maintain a `dummy` head for the next level.
1.  Iterate current level using `curr = curr.next`.
2.  If `curr.left`: attach to `dummy` list.
3.  If `curr.right`: attach to `dummy` list.
4.  Once current level finished, move `curr` to `dummy.next` (start of next level). Reset `dummy`.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
curr = root
next_head = None # Head of next level
prev = None # Tail of next level list

While curr:
    next_head = Node(0) # Dummy
    prev = next_head
    
    # Traverse current level
    while curr:
        if curr.left:
            prev.next = curr.left
            prev = prev.next
        if curr.right:
            prev.next = curr.right
            prev = prev.next
        curr = curr.next
    
    # Move to next level
    curr = next_head.next
```

---

## 4. Optimal Code (Python)

```python
"""
# Definition for a Node.
class Node:
    def __init__(self, val: int = 0, left: 'Node' = None, right: 'Node' = None, next: 'Node' = None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next
"""

class Solution:
    def connect(self, root: 'Node') -> 'Node':
        if not root:
            return None
            
        curr = root
        
        while curr:
            dummy = Node(0)
            tail = dummy
            
            # Traverse the current level and link the next level
            while curr:
                if curr.left:
                    tail.next = curr.left
                    tail = tail.next
                if curr.right:
                    tail.next = curr.right
                    tail = tail.next
                    
                curr = curr.next
                
            # Move to the start of the next level
            curr = dummy.next
            
        return root
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`1 -> (2, 3) -> (4, 5, #, 7)`

1.  Level 0: `Curr=1`. `Dummy` node created.
2.  `1.left(2)` -> `Dummy -> 2`. `Tail=2`.
3.  `1.right(3)` -> `Dummy -> 2 -> 3`. `Tail=3`.
4.  `1` done. `Curr = Dummy.next` (2).
5.  Level 1: `Curr=2`. `Dummy` reset.
6.  `2.left(4)` -> `Dummy -> 4`.
7.  `2.right(5)` -> `Dummy -> 4 -> 5`.
8.  `Curr` moves to `3` (via `next` pointer established in step 3).
9.  `3.left` is Null.
10. `3.right(7)` -> `Dummy -> 4 -> 5 -> 7`.
11. `Curr` done. Move to `next` level (4).
