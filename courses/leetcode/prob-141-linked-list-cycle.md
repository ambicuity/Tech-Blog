---
layout: page
title: "141. Linked List Cycle"
permalink: /courses/leetcode/prob-141-linked-list-cycle/
---

# 141. Linked List Cycle

## 1. The Question
Given `head`, the head of a linked list, determine if the linked list has a cycle in it.

There is a cycle in a linked list if there is some node in the list that can be reached again by continuously following the `next` pointer. Internally, `pos` is used to denote the index of the node that tail's `next` pointer is connected to. **Note that `pos` is not passed as a parameter**.

Return `true` if there is a cycle in the linked list. Otherwise, return `false`.

### Example 1
**Input**: `head = [3,2,0,-4], pos = 1`
**Output**: `true`
**Explanation**: There is a cycle in the linked list, where the tail connects to the 1st node (0-indexed).

### Example 2
**Input**: `head = [1,2], pos = 0`
**Output**: `true`

### Example 3
**Input**: `head = [1], pos = -1`
**Output**: `false`

---

## 2. Explanation
This is the standard **Floyd's Cycle-Finding Algorithm** (Tortoise and Hare).

### Approach: Fast and Slow Pointers
1.  Initialize `slow` and `fast` pointers to `head`.
2.  Move `slow` by 1 step, `fast` by 2 steps.
3.  If `fast` meets `slow`, there is a cycle.
4.  If `fast` reaches `None` (end of list), there is no cycle.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
If head is None: Return False
slow = head
fast = head

While fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    
    if slow == fast:
        Return True

Return False
```

---

## 4. Optimal Code (Python)

```python
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        if not head:
            return False
            
        slow = head
        fast = head
        
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            
            if slow == fast:
                return True
                
        return False
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`3 -> 2 -> 0 -> -4 -> (back to 2)`

1.  S=3, F=3.
2.  S=2, F=0.
3.  S=0, F=2.
4.  S=-4, F=-4. **Match!** Return True.
