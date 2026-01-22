---
layout: page
title: "380. Insert Delete GetRandom O(1)"
permalink: /courses/leetcode/prob-380-insert-delete-getrandom/
---

# 380. Insert Delete GetRandom O(1)

## 1. The Question
Implement the `RandomizedSet` class:
-   `RandomizedSet()` Initializes the `RandomizedSet` object.
-   `bool insert(int val)` Inserts an item `val` into the set if not present. Returns `true` if the item was not present, `false` otherwise.
-   `bool remove(int val)` Removes an item `val` from the set if present. Returns `true` if the item was present, `false` otherwise.
-   `int getRandom()` Returns a random element from the current set of elements (it's guaranteed that at least one element exists when this method is called). Each element must have the **same probability** of being returned.

You must implement the functions of the class such that each function works in **average** $O(1)$ time complexity.

### Example
**Input**:
`["RandomizedSet", "insert", "remove", "insert", "getRandom", "remove", "insert", "getRandom"]`
`[[], [1], [2], [2], [], [1], [2], []]`

**Output**:
`[null, true, false, true, 2, true, false, 2]`

---

## 2. Explanation
We need three operations in $O(1)$:
1.  **Insert**: Hash Map is ideal for $O(1)$ check and insert.
2.  **Remove**: Hash Map allows $O(1)$ remove, but we also need `getRandom`.
3.  **GetRandom**: We need to pick an index uniformly at random. Arrays (Lists) are best for this (`list[random_index]`).

**The Problem**: Removing from the middle of an array is $O(n)$ because elements shift.
**The Solution**: "Swap and Pop".
-   To remove element `X`:
    1.  Find `X`'s index using a Hash Map.
    2.  Swap `X` with the **last** element in the array.
    3.  Pop the last element.
    4.  Update the Hash Map for the moved last element.

This keeps the array contiguous (no gaps) so `getRandom` stays valid.

---

## 3. Pseudo Code
```text
Class RandomizedSet:
    map = {}    # val -> index
    list = []   # values

    Function insert(val):
        If val in map: Return False
        map[val] = length(list)
        list.append(val)
        Return True

    Function remove(val):
        If val not in map: Return False
        idx = map[val]
        last_val = list[-1]
        
        # Move last val to idx
        list[idx] = last_val
        map[last_val] = idx
        
        # Remove old last (which is now garbage val)
        list.pop()
        del map[val]
        Return True

    Function getRandom():
        idx = random(0, length(list) - 1)
        Return list[idx]
```

---

## 4. Optimal Code (Python)

```python
import random

class RandomizedSet:

    def __init__(self):
        self.val_map = {} # val -> index
        self.val_list = []

    def insert(self, val: int) -> bool:
        if val in self.val_map:
            return False
            
        # Add to end of list and record index
        self.val_map[val] = len(self.val_list)
        self.val_list.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.val_map:
            return False
            
        # Get index of element to remove
        idx = self.val_map[val]
        last_val = self.val_list[-1]
        
        # Place last element in the hole
        self.val_list[idx] = last_val
        self.val_map[last_val] = idx
        
        # Remove the last element
        self.val_list.pop()
        del self.val_map[val]
        return True

    def getRandom(self) -> int:
        return random.choice(self.val_list)
```

---

## 5. Complexity
-   **Time**: All operations are $O(1)$ on average.
-   **Space**: $O(n)$ to store the elements.

## 6. Example Walkthrough
`insert(10)`, `insert(20)`, `insert(30)`.
-   List: `[10, 20, 30]`
-   Map: `{10: 0, 20: 1, 30: 2}`

`remove(20)`:
1.  Target `20` is at index `1`.
2.  Last element is `30`.
3.  Overwrite index `1` with `30`: List becomes `[10, 30, 30]`.
4.  Update map for `30`: `{10: 0, 20: 1, 30: 1}`.
5.  Pop list: `[10, 30]`.
6.  Delete `20` from map: `{10: 0, 30: 1}`.
    Done.
