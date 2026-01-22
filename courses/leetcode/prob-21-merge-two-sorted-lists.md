---
layout: page
title: "21. Merge Two Sorted Lists"
permalink: /courses/leetcode/prob-21-merge-two-sorted-lists/
---

# 21. Merge Two Sorted Lists

## 1. The Question
You are given the heads of two sorted linked lists `list1` and `list2`.

Merge the two lists in a one **sorted** list. The list should be made by splicing together the nodes of the first two lists.

Return the head of the merged linked list.

### Example 1
**Input**: `list1 = [1,2,4], list2 = [1,3,4]`
**Output**: `[1,1,2,3,4,4]`

### Example 2
**Input**: `list1 = [], list2 = []`
**Output**: `[]`

### Example 3
**Input**: `list1 = [], list2 = [0]`
**Output**: `[0]`

---

## 2. Explanation
This is the standard merge step of Merge Sort.
1.  Create a dummy node.
2.  Compare heads of `l1` and `l2`.
3.  Attach smallest to `curr.next`.
4.  Advance pointers.
5.  If one list is exhausted, attach the rest of the other list.

-   **Time**: $O(N + M)$.
-   **Space**: $O(1)$. We reuse existing nodes.

---

## 3. Pseudo Code
```text
dummy = ListNode(0)
curr = dummy

While list1 and list2:
    if list1.val < list2.val:
        curr.next = list1
        list1 = list1.next
    else:
        curr.next = list2
        list2 = list2.next
    curr = curr.next

if list1: curr.next = list1
if list2: curr.next = list2

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
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0)
        curr = dummy
        
        while list1 and list2:
            if list1.val < list2.val:
                curr.next = list1
                list1 = list1.next
            else:
                curr.next = list2
                list2 = list2.next
            curr = curr.next
            
        # Attach remaining
        if list1:
            curr.next = list1
        elif list2:
            curr.next = list2
            
        return dummy.next
```

---

## 5. Complexity
-   **Time**: $O(N + M)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`l1=[1,2,4], l2=[1,3,4]`

1.  `1` vs `1`. Pick `l1(1)`. `l1` at 2. Res: `[1]`.
2.  `2` vs `1`. Pick `l2(1)`. `l2` at 3. Res: `[1,1]`.
3.  `2` vs `3`. Pick `l1(2)`. `l1` at 4. Res: `[1,1,2]`.
4.  `4` vs `3`. Pick `l2(3)`. `l2` at 4. Res: `[1,1,2,3]`.
5.  `4` vs `4`. Pick `l1(4)`. `l1` empty. Res: `[1,1,2,3,4]`.
6.  `l1` empty. Attach `l2([4])`. Res: `[1,1,2,3,4,4]`.
