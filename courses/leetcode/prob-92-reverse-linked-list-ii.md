---
layout: page
title: "92. Reverse Linked List II"
permalink: /courses/leetcode/prob-92-reverse-linked-list-ii/
---

# 92. Reverse Linked List II

## 1. The Question
Given the `head` of a singly linked list and two integers `left` and `right` where `left <= right`, reverse the nodes of the list from position `left` to position `right`, and return the reversed list.

### Example 1
**Input**: `head = [1,2,3,4,5], left = 2, right = 4`
**Output**: `[1,4,3,2,5]`

### Example 2
**Input**: `head = [5], left = 1, right = 1`
**Output**: `[5]`

---

## 2. Explanation
We need to reverse a sub-segment of the list.
1.  Navigate to the node just before `left` (let's call it `pre`).
2.  `curr` is at `left`.
3.  We need to reverse `right - left` links.
    -   Standard reverse logic: Insert `curr.next` to the front (after `pre`).

**Strategy**: "Extraction and Insertion".
`pre -> 2(curr) -> 3(next) -> 4 -> 5`
Move `3` to after `pre`:
`pre -> 3 -> 2 -> 4 -> 5`
Move `4` to after `pre`:
`pre -> 4 -> 3 -> 2 -> 5`

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
dummy = Node(0, head)
pre = dummy

# Move pre to left-1
For i from 0 to left-2:
    pre = pre.next

curr = pre.next
# Reverse for right-left times
for i from 0 to right-left-1:
    temp = curr.next
    curr.next = temp.next
    temp.next = pre.next
    pre.next = temp

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
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        if not head or left == right:
            return head
            
        dummy = ListNode(0, head)
        pre = dummy
        
        # 1. Move `pre` to the node just before the `left` position
        # We perform left - 1 jumps
        for _ in range(left - 1):
            pre = pre.next
            
        # `curr` is the first node to be reversed
        curr = pre.next
        
        # 2. Reverse the sublist
        # We need to move (right - left) nodes to the front
        num_swaps = right - left
        for _ in range(num_swaps):
            # The node we want to move to the front
            temp = curr.next
            
            # Wire curr to skip temp
            curr.next = temp.next
            
            # Wire temp to be after pre
            temp.next = pre.next
            pre.next = temp
            
        return dummy.next
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`1 -> 2 -> 3 -> 4 -> 5`, `L=2, R=4`.
`Dummy -> 1(pre) -> 2(curr) -> 3 -> 4 -> 5`.

1.  Reverse `3`:
    -   `temp = 3`.
    -   `curr.next = 4`. `2 -> 4`.
    -   `temp.next = 2`. `3 -> 2`.
    -   `pre.next = 3`. `1 -> 3`.
    Result: `1 -> 3 -> 2 -> 4 -> 5`.
2.  Reverse `4`:
    -   `temp = 4`.
    -   `curr.next = 5`. `2 -> 5`.
    -   `temp.next = 3`. `4 -> 3`.
    -   `pre.next = 4`. `1 -> 4`.
    Result: `1 -> 4 -> 3 -> 2 -> 5`. Done.
