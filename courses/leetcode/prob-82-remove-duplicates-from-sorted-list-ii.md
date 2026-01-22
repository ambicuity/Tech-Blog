---
layout: page
title: "82. Remove Duplicates from Sorted List II"
permalink: /courses/leetcode/prob-82-remove-duplicates-from-sorted-list-ii/
---

# 82. Remove Duplicates from Sorted List II

## 1. The Question
Given the `head` of a sorted linked list, delete all nodes that have duplicate numbers, leaving only distinct numbers from the original list. Return the linked list sorted as well.

### Example 1
**Input**: `head = [1,2,3,3,4,4,5]`
**Output**: `[1,2,5]`

### Example 2
**Input**: `head = [1,1,1,2,3]`
**Output**: `[2,3]`

---

## 2. Explanation
We need to remove *all* instances of duplicates. If `1` appears twice, *both* correct `1`s are removed.
Normal removal just removes duplicates and keeps one. This removes the number entirely.

Algorithm:
1.  Use `dummy` node (head might be deleted). `pre = dummy`.
2.  `dummy.next = head`.
3.  While `head` and `head.next`:
    -   If `head.val == head.next.val`:
        -   We found a duplicate block.
        -   Loop while `head.next` and `head.val == head.next.val` to find the end of block.
        -   Point `pre.next` to `head.next`. (Skip the entire block).
        -   Move `head` forward.
    -   Else:
        -   `pre = pre.next`.
        -   `head = head.next`.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
dummy = ListNode(0, head)
pre = dummy

while head:
    if head.next and head.val == head.next.val:
        # Move head until last of duplicate sequence
        while head.next and head.val == head.next.val:
            head = head.next
        
        # Skip duplicates
        pre.next = head.next
    else:
        pre = pre.next
    
    head = head.next

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
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head:
            return None
            
        dummy = ListNode(0, head)
        pre = dummy 
        
        while head:
            # If current node is start of potential duplicates
            if head.next and head.val == head.next.val:
                # Move 'head' to the last node of the duplicates sublist
                while head.next and head.val == head.next.val:
                    head = head.next
                
                # Skip all duplicates
                # pre.next was pointing to the first 'head', now point to head.next
                pre.next = head.next
            else:
                # No duplicate for current head, move pre forward
                pre = pre.next
                
            head = head.next
            
        return dummy.next
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`1 -> 2 -> 3 -> 3 -> 4`.

1.  `Pre=Dummy`, `Head=1`. Distinct. `Pre=1`. `Head=2`.
2.  `Head=2`. Distinct. `Pre=2`. `Head=3`.
3.  `Head=3`. Next is 3. Duplicate!
    -   Loop until last 3. `Head` at second 3.
    -   `Pre.next` (was 3) -> `Head.next` (4). List: `1->2->4`.
    -   `Head` moves to 4.
4.  `Head=4`. Distinct. `Pre=4`. `Head=None`.
5.  End.
