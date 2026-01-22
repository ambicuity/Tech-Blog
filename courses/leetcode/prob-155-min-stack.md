---
layout: page
title: "155. Min Stack"
permalink: /courses/leetcode/prob-155-min-stack/
---

# 155. Min Stack

## 1. The Question
Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.

Implement the `MinStack` class:
-   `MinStack()` initializes the stack object.
-   `void push(int val)` pushes the element `val` onto the stack.
-   `void pop()` removes the element on the top of the stack.
-   `int top()` gets the top element of the stack.
-   `int getMin()` retrieves the minimum element in the stack.

You must implement a solution with `O(1)` time complexity for each function.

### Example 1
**Input**
`["MinStack","push","push","push","getMin","pop","top","getMin"]`
`[[],[-2],[0],[-3],[],[],[],[]]`

**Output**
`[null,null,null,null,-3,null,0,-2]`

---

## 2. Explanation
Standard stack operations are $O(1)$. The challenge is `getMin()` in $O(1)$.
If we just keep a variable `min_val`, it works for push, but when we **pop** the minimum value, we don't know what the *previous* minimum was.

### Approach 1: Two Stacks
1.  `stack`: Stores actual values.
2.  `min_stack`: Stores the minimum value *at that level*.
    -   Push `val`: Push `val` to `stack`. Push `min(val, min_stack.top())` to `min_stack`.
    -   Pop: Pop both.
    -   GetMin: Return `min_stack.top()`.

This guarantees that for every element in the main stack, we know what the minimum was when that element was added.

-   **Time**: $O(1)$ all ops.
-   **Space**: $O(N)$ (double the space).

---

## 3. Pseudo Code
```text
class MinStack:
    stack = []
    min_stack = []

    push(val):
        stack.push(val)
        if min_stack.empty or val < min_stack.peek():
            min_stack.push(val)
        else:
            min_stack.push(min_stack.peek())

    pop():
        stack.pop()
        min_stack.pop()

    getMin():
        return min_stack.peek()
```

---

## 4. Optimal Code (Python)

```python
class MinStack:

    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        
        # Determine the current minimum
        if not self.min_stack:
            val_to_push = val
        else:
            val_to_push = min(val, self.min_stack[-1])
            
        self.min_stack.append(val_to_push)

    def pop(self) -> None:
        self.stack.pop()
        self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]
```

---

## 5. Complexity
-   **Time**: $O(1)$ for all operations.
-   **Space**: $O(N)$ auxiliary stack.

## 6. Example Walkthrough
1.  Push -2. `St: [-2]`, `Mn: [-2]`.
2.  Push 0. `St: [-2, 0]`. `Mn: [-2, -2]`. (0 > -2).
3.  Push -3. `St: [-2, 0, -3]`. `Mn: [-2, -2, -3]`.
4.  GetMin: -3.
5.  Pop. `St: [-2, 0]`. `Mn: [-2, -2]`.
6.  GetMin: -2.
