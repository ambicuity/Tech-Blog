---
layout: page
title: "146. LRU Cache"
permalink: /courses/leetcode/prob-146-lru-cache/
---

# 146. LRU Cache

## 1. The Question
Design a data structure that follows the constraints of a **Least Recently Used (LRU) cache**.

Implement the `LRUCache` class:
-   `LRUCache(int capacity)` Initialize the LRU cache with positive size `capacity`.
-   `int get(int key)` Return the value of the `key` if the key exists, otherwise return `-1`.
-   `void put(int key, int value)` Update the value of the `key` if the `key` exists. Otherwise, add the `key-value` pair to the cache. If the number of keys exceeds the `capacity` from this operation, **evict** the least recently used key.

The functions `get` and `put` must each run in `O(1)` average time complexity.

### Example 1
**Input**
`["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]`
`[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]`
**Output**
`[null, null, null, 1, null, -1, null, -1, 3, 4]`

---

## 2. Explanation
To achieve $O(1)$ for both `get` and `put`, and to maintain order of usage:
1.  **Hash Map**: For fast lookup `key -> node`.
2.  **Doubly Linked List**: For maintaining usage order.
    -   Head: Most recently used.
    -   Tail: Least recently used (to be evicted).
    -   Why doubly? Because when we access a node in the middle, we need to remove it and move it to the head. Removing a node requires access to its `prev`, which doubly linked list provides in $O(1)$.

**Operations**:
-   `get(key)`:
    -   If not in map, return -1.
    -   Else, move node to Head (mark as recently used). Return val.
-   `put(key, val)`:
    -   If key exists: Update val, move to Head.
    -   If key new: Create node, add to Head, add to Map.
        -   If size > cap: Remove Tail, remove from Map.

-   **Time**: $O(1)$.
-   **Space**: $O(C)$ where C is capacity.

---

## 3. Pseudo Code
```text
class Node: prev, next, key, val

class LRUCache:
    map = {}
    head, tail (dummies)
    
    _remove(node):
        node.prev.next = node.next
        node.next.prev = node.prev
        
    _add(node):
        # Add to front (after head)
        node.prev = head
        node.next = head.next
        head.next.prev = node
        head.next = node
        
    get(key):
        if key in map:
            node = map[key]
            _remove(node)
            _add(node)
            return node.val
        return -1
        
    put(key, value):
        if key in map:
            _remove(map[key])
        
        node = Node(key, value)
        _add(node)
        map[key] = node
        
        if len(map) > cap:
            lru = tail.prev
            _remove(lru)
            del map[lru.key]
```

---

## 4. Optimal Code (Python)

```python
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        # Hash Map: key -> Node
        self.cache = {}
        
        # Doubly Linked List with Dummy Head (MRU) and Tail (LRU)
        # Head -> Most Recent ... -> Least Recent -> Tail
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        """Remove node from linked list."""
        prev = node.prev
        nxt = node.next
        prev.next = nxt
        nxt.prev = prev

    def _add(self, node):
        """Add node right after head (Most Recent)."""
        nxt = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = nxt
        nxt.prev = node

    def get(self, key: int) -> int:
        if key in self.cache:
            node = self.cache[key]
            # Move to front
            self._remove(node)
            self._add(node)
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing
            self._remove(self.cache[key])
        
        node = Node(key, value)
        self._add(node)
        self.cache[key] = node
        
        # Evict if over capacity
        if len(self.cache) > self.capacity:
            # LRU is the node before tail
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
```

---

## 5. Complexity
-   **Time**: $O(1)$ for get and put.
-   **Space**: $O(C)$.

## 6. Example Walkthrough
`Cap = 2`. `Head <-> Tail`.

1.  Put(1, 1). `H <-> 1 <-> T`. Map:{1}.
2.  Put(2, 2). `H <-> 2 <-> 1 <-> T`. Map:{1, 2}.
3.  Get(1). Move 1 to front. `H <-> 1 <-> 2 <-> T`. Return 1.
4.  Put(3, 3). Cap exceeded. Remove LRU (before Tail: 2).
    -   Add 3. `H <-> 3 <-> 1 <-> T`. Map:{1, 3}.
5.  Get(2). Not in map. Return -1.
