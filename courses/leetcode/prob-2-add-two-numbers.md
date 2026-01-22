---
layout: page
title: "2. Add Two Numbers"
permalink: /courses/leetcode/prob-2-add-two-numbers/
---

# 2. Add Two Numbers

## 1. The Question
You are given two **non-empty** linked lists representing two non-negative integers. The digits are stored in **reverse order**, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.

### Example 1
**Input**: `l1 = [2,4,3], l2 = [5,6,4]`
**Output**: `[7,0,8]`
**Explanation**: 342 + 465 = 807.

### Example 2
**Input**: `l1 = [0], l2 = [0]`
**Output**: `[0]`

### Example 3
**Input**: `l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]`
**Output**: `[8,9,9,9,0,0,0,1]`

---

## 2. Explanation
We perform addition exactly like we do on paper (from right to left). Since the lists are reversed, the heads are the least significant digits, which is perfect.

1.  Initialize a dummy head for result.
2.  `carry = 0`.
3.  Loop while `l1` or `l2` or `carry`:
    -   `sum = carry`.
    -   If `l1`: `sum += l1.val`, `l1 = l1.next`.
    -   If `l2`: `sum += l2.val`, `l2 = l2.next`.
    -   `carry = sum // 10`.
    -   `digit = sum % 10`.
    -   Append `digit` to result list.
4.  Return dummy.next.

-   **Time**: $O(\max(N, M))$.
-   **Space**: $O(\max(N, M))$ for the new list.

---

## 3. Pseudo Code
```text
dummy = ListNode(0)
curr = dummy
carry = 0

While l1 or l2 or carry:
    val1 = l1.val if l1 else 0
    val2 = l2.val if l2 else 0
    
    total = val1 + val2 + carry
    carry = total // 10
    curr.next = ListNode(total % 10)
    curr = curr.next
    
    if l1: l1 = l1.next
    if l2: l2 = l2.next

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
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0)
        curr = dummy
        carry = 0
        
        while l1 or l2 or carry:
            val1 = l1.val if l1 else 0
            val2 = l2.val if l2 else 0
            
            total = val1 + val2 + carry
            carry = total // 10
            
            curr.next = ListNode(total % 10)
            curr = curr.next
            
            if l1:
                l1 = l1.next
            if l2:
                l2 = l2.next
                
        return dummy.next
```

---

## 5. Complexity
-   **Time**: $O(\max(M, N))$.
-   **Space**: $O(\max(M, N))$ to store result.

## 6. Example Walkthrough
`l1=[2,4,3] (342)`, `l2=[5,6,4] (465)`

1.  `2 + 5 = 7`. Carry=0. List: `[7]`.
2.  `4 + 6 = 10`. Carry=1. List: `[7, 0]`.
3.  `3 + 4 + 1(carry) = 8`. Carry=0. List: `[7, 0, 8]`.
4.  End.

Result: `[7,0,8]` (807).
