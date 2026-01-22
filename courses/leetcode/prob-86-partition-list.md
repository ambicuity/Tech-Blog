---
layout: page
title: "86. Partition List"
permalink: /courses/leetcode/prob-86-partition-list/
---

# 86. Partition List

## 1. The Question
Given the `head` of a linked list and a value `x`, partition it such that all nodes **less than** `x` come before nodes **greater than or equal** to `x`.

You should **preserve the original relative order** of the nodes in each of the two partitions.

### Example 1
**Input**: `head = [1,4,3,2,5,2], x = 3`
**Output**: `[1,2,2,4,3,5]`

### Example 2
**Input**: `head = [2,1], x = 2`
**Output**: `[1,2]`

---

## 2. Explanation
We need to split the list into two:
1.  `small_list`: nodes < x.
2.  `large_list`: nodes >= x.
Then concatenate them: `small_list_tail.next = large_list_head`.

Algorithm:
1.  Create two dummy heads: `before_head` and `after_head`.
2.  Pointers `before` and `after`.
3.  Iterate through the list.
    -   If `val < x`: Append to `before`.
    -   Else: Append to `after`.
4.  Join lists.
5.  Important: Set `after.next = None` to avoid cycles.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
before_head = Node(0)
after_head = Node(0)
before = before_head
after = after_head

while head:
    if head.val < x:
        before.next = head
        before = before.next
    else:
        after.next = head
        after = after.next
        
    head = head.next

after.next = None
before.next = after_head.next

return before_head.next
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
    def partition(self, head: Optional[ListNode], x: int) -> Optional[ListNode]:
        before_head = ListNode(0)
        after_head = ListNode(0)
        
        before = before_head
        after = after_head
        
        while head:
            if head.val < x:
                before.next = head
                before = before.next
            else:
                after.next = head
                after = after.next
                
            head = head.next
            
        # Terminate the after list to prevent cycles
        after.next = None
        
        # Join the two lists
        before.next = after_head.next
        
        return before_head.next
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`1 -> 4 -> 3 -> 2 -> 5 -> 2`, `x=3`

1.  `1 < 3`. Before: `[1]`.
2.  `4 >= 3`. After: `[4]`.
3.  `3 >= 3`. After: `[4, 3]`.
4.  `2 < 3`. Before: `[1, 2]`.
5.  `5 >= 3`. After: `[4, 3, 5]`.
6.  `2 < 3`. Before: `[1, 2, 2]`.

Join: `[1,2,2]` -> `[4,3,5]`.
Result: `[1,2,2,4,3,5]`.
