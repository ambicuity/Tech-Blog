---
layout: page
title: "23. Merge k Sorted Lists"
permalink: /courses/leetcode/prob-23-merge-k-sorted-lists/
---

# 23. Merge k Sorted Lists

## 1. The Question
You are given an array of `k` linked-lists `lists`, each linked-list is sorted in ascending order.

Merge all the linked-lists into one sorted linked-list and return it.

### Example 1
**Input**: `lists = [[1,4,5],[1,3,4],[2,6]]`
**Output**: `[1,1,2,3,4,4,5,6]`
**Explanation**: The lists are:
[
  1->4->5,
  1->3->4,
  2->6
]
merging them into one sorted list:
1->1->2->3->4->4->5->6

---

## 2. Explanation
This is an extension of "Merge Two Sorted Lists".
Naive: Merge list 1 and 2, then result with 3... Time: $O(k \cdot N)$. Too slow.

### Approach 1: Min-Heap
Keep the `head` of every list in a Min-Heap.
1.  Pop smallest element. Append to result.
2.  Push `next` of that element into Heap.
-   **Time**: $O(N \log k)$, where N is total nodes.
-   **Space**: $O(k)$ for heap.

### Approach 2: Divide and Conquer
Pair up lists and merge them.
reduce k lists -> k/2 lists -> k/4 ... -> 1 list.
-   **Time**: $O(N \log k)$.
-   **Space**: $O(1)$ (iterative) or $O(\log k)$ (recursive).

We will use **Min-Heap** as it is very intuitive for "k sorted streams".

---

## 3. Pseudo Code
```text
heap = []
for l in lists:
    if l: heappush(heap, (l.val, i, l))

dummy = Node(0)
curr = dummy

while heap:
    val, idx, node = heappop(heap)
    curr.next = node
    curr = curr.next
    
    if node.next:
        heappush(heap, (node.next.val, idx, node.next))

return dummy.next
```

---

## 4. Optimal Code (Python)

```python
import heapq

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:
    def mergeKLists(self, lists: list[Optional[ListNode]]) -> Optional[ListNode]:
        heap = []
        
        # Initialize heap. 
        # Note: We include 'i' in the tuple to handle tie-breaking for values.
        # Python compares tuples element by element. If values are same, it compares 'i'.
        # Since 'i' is unique, it never compares ListNode (which would crash).
        for i, l in enumerate(lists):
            if l:
                heapq.heappush(heap, (l.val, i, l))
                
        dummy = ListNode(0)
        curr = dummy
        
        while heap:
            val, i, node = heapq.heappop(heap)
            curr.next = node
            curr = curr.next
            
            if node.next:
                heapq.heappush(heap, (node.next.val, i, node.next))
                
        return dummy.next
```

---

## 5. Complexity
-   **Time**: $O(N \log k)$. N = Total nodes.
-   **Space**: $O(k)$.

## 6. Example Walkthrough
`[1,4,5], [1,3,4], [2,6]`
Heap: `[(1, 0, Node(1)), (1, 1, Node(1)), (2, 2, Node(2))]`
1.  Pop `(1, 0)`. Res `1`. Push `(4, 0)`. Heap `[(1,1), (2,2), (4,0)]`.
2.  Pop `(1, 1)`. Res `1-1`. Push `(3, 1)`. Heap `[(2,2), (3,1), (4,0)]`.
3.  Pop `(2, 2)`. Res `1-1-2`. Push `(6, 2)`.
...
