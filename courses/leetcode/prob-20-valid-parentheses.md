---
layout: page
title: "20. Valid Parentheses"
permalink: /courses/leetcode/prob-20-valid-parentheses/
---

# 20. Valid Parentheses

## 1. The Question
Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.

An input string is valid if:
1.  Open brackets must be closed by the same type of brackets.
2.  Open brackets must be closed in the correct order.
3.  Every close bracket has a corresponding open bracket of the same type.

### Example 1
**Input**: `s = "()"`
**Output**: `true`

### Example 2
**Input**: `s = "()[]{}"`
**Output**: `true`

### Example 3
**Input**: `s = "(]"`
**Output**: `false`

### Example 4
**Input**: `s = "([])"`
**Output**: `true`

---

## 2. Explanation
This is a classic Stack problem.
We process the string from left to right.
-   When we see an **open** bracket, we push it onto the stack. They wait to be closed.
-   When we see a **close** bracket, it must close the *most recently opened* bracket (LIFO).
    -   If stack is empty, return False (unmatched close).
    -   Pop top of stack. If it doesn't match the current close bracket, return False.

At the end, stack must be empty (all opened brackets were closed).

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
stack = []
map = {')':'(', '}':'{', ']':'['}

For char in s:
    If char in map: # Closing bracket
        top = stack.pop() if stack else '#'
        if map[char] != top:
            Return False
    Else: # Opening bracket
        stack.append(char)

Return stack.isEmpty()
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        mapping = {")": "(", "}": "{", "]": "["}
        
        for char in s:
            if char in mapping:
                # Top element of stack if not empty, else dummy value
                top_element = stack.pop() if stack else '#'
                
                # If the mapping for this bracket doesn't match the stack's top element
                if mapping[char] != top_element:
                    return False
            else:
                # We have an opening bracket, push to stack
                stack.append(char)
                
        # Return True if the stack is exhausted
        return not stack
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`s = "([])"`

1.  `(`: Push. Stack: `['(']`.
2.  `[`: Push. Stack: `['(', '[']`.
3.  `]`: Close. Pop `[`. Matches `[`? Yes. Stack: `['(']`.
4.  `)`: Close. Pop `(`. Matches `(`? Yes. Stack: `[]`.
5.  End: Stack empty. Return True.
