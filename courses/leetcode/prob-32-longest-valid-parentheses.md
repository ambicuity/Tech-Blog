---
layout: page
title: "32. Longest Valid Parentheses"
permalink: /courses/leetcode/prob-32-longest-valid-parentheses/
---

# 32. Longest Valid Parentheses

## 1. The Question
Given a string containing just the characters `'('` and `')'`, return the length of the longest valid (well-formed) parentheses substring.

### Example 1
**Input**: `s = "(()"`
**Output**: `2`
**Explanation**: The longest valid parentheses substring is "()".

### Example 2
**Input**: `s = ")()())"`
**Output**: `4`
**Explanation**: The longest valid parentheses substring is "()()".

---

## 2. Explanation
Method 1: **Stack**.
Push indices.
Initialize stack with `-1` (base for calculation).
-   If `(`: push index.
-   If `)`: pop.
    -   If stack empty: push current index (replacement for base).
    -   Else: `ans = max(ans, current_index - stack.top())`.
Time $O(N)$, Space $O(N)$.

Method 2: **Two Pass Counters** ($O(1)$ space).
Left to Right:
-   Count `(` and `)`.
-   If `left == right`, `len = 2 * right`. Maximize logic.
-   If `right > left`, invalid. Reset counters.
Right to Left:
-   Similar logic (If `left > right`, invalid).
This covers cases like `(()`.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
left = right = max_len = 0
for c in s:
    if c == '(': left += 1
    else: right += 1
    if left == right: max_len = max(max_len, 2 * right)
    elif right > left: left = right = 0

left = right = 0
for c in reversed(s):
    if c == '(': left += 1
    else: right += 1
    if left == right: max_len = max(max_len, 2 * left)
    elif left > right: left = right = 0
    
return max_len
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def longestValidParentheses(self, s: str) -> int:
        left = right = max_len = 0
        
        # Left to Right Scan
        for char in s:
            if char == '(':
                left += 1
            else:
                right += 1
            
            if left == right:
                max_len = max(max_len, 2 * right)
            elif right > left:
                left = right = 0
        
        # Right to Left Scan
        left = right = 0
        for char in reversed(s):
            if char == '(':
                left += 1
            else:
                right += 1
                
            if left == right:
                max_len = max(max_len, 2 * left)
            elif left > right:
                left = right = 0
                
        return max_len
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`(()`
L->R:
1.  `(`: L=1, R=0.
2.  `(`: L=2, R=0.
3.  `)`: L=2, R=1.
No update (L!=R). End. Ans=0.
R->L:
1.  `)`: L=0, R=1. `L<R?` No. `L>R?` No.
2.  `(`: L=1, R=1. Max=2.
3.  `(`: L=2, R=1. `L>R`? Yes. Reset.
Return 2.
Wait, R->L logic: `(` increases `left`? Yes. `)` increases `right`? Yes.
So index 2 `)` -> R=1. L=0.
Index 1 `(` -> L=1. L=R. Max=2.
Index 0 `(` -> L=2. L>R. Reset.
Correct.
