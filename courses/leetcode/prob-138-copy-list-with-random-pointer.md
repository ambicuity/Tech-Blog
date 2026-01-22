---
layout: page
title: "138. Copy List with Random Pointer"
permalink: /courses/leetcode/prob-138-copy-list-with-random-pointer/
---

# 138. Copy List with Random Pointer

## 1. The Question
A linked list of length `n` is given such that each node contains an additional random pointer, which could point to any node in the list, or `null`.

Construct a **deep copy** of the list. The deep copy should consist of exactly `n` brand new nodes, where each new node has its value set to the value of its corresponding original node. Both the `next` and `random` pointer of the new nodes should point to new nodes in the copied list such that the pointers in the original list and copied list represent the same list state. None of the pointers in the new list should point to nodes in the original list.

Return the head of the copied linked list.

### Example 1
**Input**: `head = [[7,null],[13,0],[11,4],[10,2],[1,0]]`
**Output**: `[[7,null],[13,0],[11,4],[10,2],[1,0]]`

---

## 2. Explanation
We need to clone nodes and also their connections (`next` and `random`).
The tricky part is that `random` acts as arbitrary edges.

### Approach 1: Hash Map
Use a map `old_node -> new_node`.
1.  Pass 1: Create all new nodes and store in map.
2.  Pass 2: Connect `next` and `random` using the map.
    -   `map[old].next = map[old.next]`
    -   `map[old].random = map[old.random]`

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

### Approach 2: Interweaving Nodes (Optimal Space)
1.  Insert new nodes *between* old nodes.
    `A -> A' -> B -> B' -> C -> C'`
2.  Copy random pointers.
    `A'.random = A.random.next` (if A.random exists).
3.  Separate the lists.
    Restore `A -> B` and extract `A' -> B'`.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$ (excluding result).

We will implement **Approach 1** (Hash Map) as it is much more intuitive and standard for interview settings unless $O(1)$ spacce is strictly required.

---

## 3. Pseudo Code
```text
if not head: return None
map = {}

curr = head
while curr:
    map[curr] = Node(curr.val)
    curr = curr.next

curr = head
while curr:
    new_node = map[curr]
    new_node.next = map[curr.next] if curr.next else None
    new_node.random = map[curr.random] if curr.random else None
    curr = curr.next

return map[head]
```

---

## 4. Optimal Code (Python)

```python
"""
# Definition for a Node.
class Node:
    def __init__(self, x: int, next: 'Node' = None, random: 'Node' = None):
        self.val = int(x)
        self.next = next
        self.random = random
"""

class Solution:
    def copyRandomList(self, head: 'Optional[Node]') -> 'Optional[Node]':
        if not head:
            return None
            
        old_to_new = {}
        
        # 1. Create all nodes
        curr = head
        while curr:
            old_to_new[curr] = Node(curr.val)
            curr = curr.next
            
        # 2. Connect pointers
        curr = head
        while curr:
            new_node = old_to_new[curr]
            new_node.next = old_to_new.get(curr.next)
            new_node.random = old_to_new.get(curr.random)
            curr = curr.next
            
        return old_to_new[head]
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`A(7, null) -> B(13, A) -> C(11, B)`

1.  Map: `{A: A', B: B', C: C'}`.
2.  `A'`: next=B', random=None.
3.  `B'`: next=C', random=A'.
4.  `C'`: next=None, random=B'.
