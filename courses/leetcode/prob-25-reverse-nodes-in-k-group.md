---
layout: page
title: "25. Reverse Nodes in k-Group"
permalink: /courses/leetcode/prob-25-reverse-nodes-in-k-group/
---

# 25. Reverse Nodes in k-Group

## 1. The Question
Given the `head` of a linked list, reverse the nodes of the list `k` at a time, and return the modified list.

`k` is a positive integer and is less than or equal to the length of the linked list. If the number of nodes is not a multiple of `k` then left-out nodes, in the end, should remain as it is.

You may not alter the values in the list's nodes, only nodes themselves may be changed.

### Example 1
**Input**: `head = [1,2,3,4,5], k = 2`
**Output**: `[2,1,4,3,5]`

### Example 2
**Input**: `head = [1,2,3,4,5], k = 3`
**Output**: `[3,2,1,4,5]`

---

## 2. Explanation
This is a Hard version of "Reverse Linked List II".
We repeatedly reverse subsegments of size `k`.
We need to check if there are at least `k` nodes left. If not, don't reverse.

Algorithm:
1.  Count total nodes `n`.
2.  Iterate `n // k` times.
3.  In each iteration, perform the "Reverse Sublist" logic (same as Q92) for `k-1` swaps.
4.  Advance pointers. `pre` becomes the `tail` of the newly reversed section (which was the `curr`). `curr` becomes the next node.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
n = count_nodes(head)
dummy = Node(0, head)
pre = dummy
curr = head

For group in range(n // k):
    # Reverse k nodes (perform k-1 swaps)
    for i in range(k-1):
        temp = curr.next
        curr.next = temp.next
        temp.next = pre.next
        pre.next = temp
    
    # Move pre to the end of the reversed group
    pre = curr
    curr = curr.next

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
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if not head or k == 1:
            return head
            
        dummy = ListNode(0, head)
        
        # 1. Count nodes
        count = 0
        curr = head
        while curr:
            count += 1
            curr = curr.next
            
        pre = dummy
        curr = head
        
        # 2. Reverse in groups
        for _ in range(count // k):
            # For a group of size k, we do k-1 swaps
            for _ in range(k - 1):
                temp = curr.next
                curr.next = temp.next
                temp.next = pre.next
                pre.next = temp
                
            # Move pre to the end of the reversed group
            # curr is now at the end of the group (it was the start before reversing)
            pre = curr
            curr = curr.next
            
        return dummy.next
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`1->2->3->4->5`, `k=2`. Count=5. Groups=2.

Group 1: `Pre=Dummy`, `Curr=1`.
-   Swap `2`. `Dummy->2->1->3`.
-   End Group. `Pre=1`. `Curr=3`.

Group 2: `Pre=1`, `Curr=3`.
-   Swap `4`. `1->4->3->5`.
-   End Group. `Pre=3`. `Curr=5`.

Remaining: `5`. `Pre=3`. Done.
Result: `2->1->4->3->5`.
