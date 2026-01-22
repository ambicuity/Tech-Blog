---
layout: page
title: "61. Rotate List"
permalink: /courses/leetcode/prob-61-rotate-list/
---

# 61. Rotate List

## 1. The Question
Given the `head` of a linked list, rotate the list to the right by `k` places.

### Example 1
**Input**: `head = [1,2,3,4,5], k = 2`
**Output**: `[4,5,1,2,3]`

### Example 2
**Input**: `head = [0,1,2], k = 4`
**Output**: `[2,0,1]`

---

## 2. Explanation
Rotating a list by `k` means moving the last `k` nodes to the front.
Or, making the `(L - k)`th node the new tail, and `(L - k + 1)`th node the new head.

Algorithm:
1.  Find length `L`.
2.  Connect the tail to `head` (make it a ring).
3.  Calculate `k = k % L`.
4.  If `k == 0`, break ring and return.
5.  Move `L - k` steps from the old tail to find the new tail.
6.  `new_head = new_tail.next`.
7.  `new_tail.next = None` (break ring).

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
if not head: return None
L = 1
tail = head
while tail.next:
    tail = tail.next
    L++

k = k % L
if k == 0: return head

tail.next = head # Ring
steps = L - k
new_tail = tail

for _ in range(steps):
    new_tail = new_tail.next

new_head = new_tail.next
new_tail.next = None

return new_head
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
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if not head or not head.next:
            return head
            
        # 1. Calculate length and find tail
        old_tail = head
        length = 1
        while old_tail.next:
            old_tail = old_tail.next
            length += 1
            
        # 2. Normalize k
        k = k % length
        if k == 0:
            return head
            
        # 3. Form a ring
        old_tail.next = head
        
        # 4. Find new tail position: (length - k - 1) steps from head
        # Or (length - k) steps from old_tail (since old_tail is at N-1)
        # Let's count from head to be safe. We need node at index (Length - k - 1).
        
        # Actually easier to use the ring:
        # Move old_tail 'Length - k' steps forward.
        new_tail = old_tail
        for _ in range(length - k):
            new_tail = new_tail.next
            
        new_head = new_tail.next
        new_tail.next = None
        
        return new_head
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`1->2->3->4->5`, `k=2`. `L=5`.

1.  Tail at 5.
2.  Ring: `5->1`.
3.  Move `5 - 2 = 3` steps.
    -   `new_tail` moves `5 -> 1 -> 2 -> 3`.
    -   `new_tail` is 3.
4.  `new_head` is 4.
5.  Break ring at 3.
Result: `4->5->1->2->3`.
