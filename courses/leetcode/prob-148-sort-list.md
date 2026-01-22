---
layout: page
title: "148. Sort List"
permalink: /courses/leetcode/prob-148-sort-list/
---

# 148. Sort List

## 1. The Question
Given the `head` of a linked list, return the list after sorting it in **ascending order**.

**Follow up**: Can you sort the linked list in `O(n log n)` time and `O(1)` memory (i.e. constant space)?

### Example 1
**Input**: `head = [4,2,1,3]`
**Output**: `[1,2,3,4]`

---

## 2. Explanation
For Linked Lists, **Merge Sort** is the preferred `O(N log N)` algorithm.
It works by splitting the list in half (using Slow/Fast pointers) and merging the sorted halves.

-   **Recursive Merge Sort**:
    -   Time: $O(N \log N)$.
    -   Space: $O(\log N)$ (stack space).
-   **Iterative Merge Sort (Bottom-Up)**:
    -   Time: $O(N \log N)$.
    -   Space: $O(1)$.

We will implement **Recursive Merge Sort** as it is concise and usually acceptable unless STRICT $O(1)$ stack space is required (which technically recursion violates).

### Approach (Recursive):
1.  Base case: If list empty or size 1, return.
2.  Find middle.
3.  Split list into two. `mid.next = None`.
4.  Recursively sort Left and Right.
5.  Merge sorted lists (standard "Merge Two Sorted Lists" problem).

---

## 3. Pseudo Code
```text
def sortList(head):
    if not head or not head.next: return head
    
    # Get Mid
    slow, fast = head, head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    mid = slow.next
    slow.next = None
    
    left = sortList(head)
    right = sortList(mid)
    
    return merge(left, right)
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
    def sortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # Base Case
        if not head or not head.next:
            return head
            
        # Split List using Slow/Fast
        # Initializing fast=head.next ensures the split happens before the middle node
        # if the list typically has even number of elements.
        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            
        mid = slow.next
        slow.next = None
        
        # Sort Halves
        left = self.sortList(head)
        right = self.sortList(mid)
        
        # Merge Halves
        return self.merge(left, right)
        
    def merge(self, l1, l2):
        dummy = ListNode(0)
        curr = dummy
        while l1 and l2:
            if l1.val < l2.val:
                curr.next = l1
                l1 = l1.next
            else:
                curr.next = l2
                l2 = l2.next
            curr = curr.next
            
        if l1: curr.next = l1
        if l2: curr.next = l2
        return dummy.next
```

---

## 5. Complexity
-   **Time**: $O(N \log N)$.
-   **Space**: $O(\log N)$ due to recursion stack.

## 6. Example Walkthrough
`[4, 2, 1, 3]`.
1.  Split: `[4, 2]` and `[1, 3]`.
    -   Sort `[4, 2]`. Split `[4]`, `[2]`. Merge -> `[2, 4]`.
    -   Sort `[1, 3]`. Split `[1]`, `[3]`. Merge -> `[1, 3]`.
2.  Merge `[2, 4]` and `[1, 3]`.
    -   `1` vs `2`. Pick `1`.
    -   `2` vs `3`. Pick `2`.
    -   `3` vs `4`. Pick `3`.
    -   `4`. Pick `4`.
    Result: `[1, 2, 3, 4]`.
