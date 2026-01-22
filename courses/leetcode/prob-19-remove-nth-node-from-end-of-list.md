---
layout: page
title: "19. Remove Nth Node From End of List"
permalink: /courses/leetcode/prob-19-remove-nth-node-from-end-of-list/
---

# 19. Remove Nth Node From End of List

## 1. The Question
Given the `head` of a linked list, remove the `nth` node from the end of the list and return its head.

### Example 1
**Input**: `head = [1,2,3,4,5], n = 2`
**Output**: `[1,2,3,5]`

### Example 2
**Input**: `head = [1], n = 1`
**Output**: `[]`

### Example 3
**Input**: `head = [1,2], n = 1`
**Output**: `[1]`

---

## 2. Explanation
To find the Nth node from the end, we can use two pointers.
1.  Move `fast` pointer `n` steps ahead.
2.  Move both `slow` and `fast` one step at a time until `fast` reaches the end.
3.  `slow` will be at the node *before* the target node (because we usually want to stop at length-n-1 to remove length-n).
    -   Wait, to remove Nth from end, we need to stop at (N+1)th from end so we can change its `next`.

Correction:
1.  Move `fast` `n+1` steps.
2.  Move `slow` and `fast`. `slow` lands just before the target.
    -   **Edge Case**: If `n` equals length of list, we are removing head. `fast` will go `n` steps and hit `None` (if we try `n+1`, we crash).
    -   Better: Use a **Dummy** node.
    -   Move `fast` `n+1` steps starting from `dummy`. This always works.

-   **Time**: $O(L)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
dummy = ListNode(0, head)
slow = dummy
fast = dummy

# Move fast n+1 steps ahead
for i in 0 to n:
    fast = fast.next

while fast:
    slow = slow.next
    fast = fast.next

# slow is before target
slow.next = slow.next.next

Return dummy.next
```

---

## 4. Optimal Code (Python)

```python
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        slow = dummy
        fast = dummy
        
        # Advance fast n+1 steps so that when fast hits end, 
        # slow is just before the node to delete.
        for _ in range(n + 1):
            fast = fast.next
            
        while fast:
            slow = slow.next
            fast = fast.next
            
        # Delete the node
        slow.next = slow.next.next
        
        return dummy.next
```

---

## 5. Complexity
-   **Time**: $O(L)$. Single pass.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`1->2->3->4->5`, `n=2`.
Dummy `0->1->2...`

1.  Fast moves 3 steps. `fast` at `3`.
2.  Slide `slow` and `fast`.
    -   `fast` at `4`, `slow` at `0`.
    -   `fast` at `5`, `slow` at `1`.
    -   `fast` at `None`, `slow` at `3`.
3.  `slow.next` is `4`. Skip it.
    -   `3->5`.
Result: `1->2->3->5`.
