---
layout: page
title: "224. Basic Calculator"
permalink: /courses/leetcode/prob-224-basic-calculator/
---

# 224. Basic Calculator

## 1. The Question
Given a string `s` representing a valid expression, implement a basic calculator to evaluate it, and return the result of the evaluation.

**Note**: You are **not** allowed to use any built-in function which evaluates strings as mathematical expressions, such as `eval()`.
The expression string may contain open `(` and closing parentheses `)`, the plus `+` or minus sign `-`, non-negative integers and empty spaces ` `.

### Example 1
**Input**: `s = "1 + 1"`
**Output**: `2`

### Example 2
**Input**: `s = " 2-1 + 2 "`
**Output**: `3`

### Example 3
**Input**: `s = "(1+(4+5+2)-3)+(6+8)"`
**Output**: `23`

---

## 2. Explanation
This is a Hard stack problem because of nested parentheses and handling unary minus or sign changes.

Unlike `Evaluate RPN` or `Basic Calculator II` (multiplication/division), here we only have `+` and `-`.
Key Idea: **Sign Distribution**.
`1 - (2 + 3)` is `1 - 2 - 3`.
We can keep a `current_sum` and a `current_sign` (+1 or -1).
When we hit `(`, we stash the `current_sum` and `current_sign` onto the stack, because the expression inside starts fresh (but the sign applies to it).

### Approach: Stack + Sign
1.  `res`: Running total. `sign`: +1 or -1. `num`: current number being built.
2.  Iterate char by char.
    -   Digit: Build `num`.
    -   `+`: Add `sign * num` to `res`. Reset `num`. Set `sign = 1`.
    -   `-`: Add `sign * num` to `res`. Reset `num`. Set `sign = -1`.
    -   `(`: Save `res` and `sign` to Stack. Reset `res = 0`, `sign = 1`.
    -   `)`: Add `sign * num` to `res` (finishing the inner expression). Now pop `prev_sign` and `prev_res`. `res = prev_res + prev_sign * res`.

-   **Time**: $O(N)$.
-   **Space**: $O(N)$ (recursion or stack).

---

## 3. Pseudo Code
```text
res = 0
sign = 1
stack = []
num = 0

For ch in s:
    if digit:
        num = num * 10 + int(ch)
    elif ch == '+':
        res += sign * num
        sign = 1
        num = 0
    elif ch == '-':
        res += sign * num
        sign = -1
        num = 0
    elif ch == '(':
        stack.push(res)
        stack.push(sign)
        res = 0
        sign = 1
    elif ch == ')':
        res += sign * num
        num = 0
        
        prev_sign = stack.pop()
        prev_res = stack.pop()
        res = prev_res + prev_sign * res

# Add remaining num if any
res += sign * num
Return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def calculate(self, s: str) -> int:
        res = 0
        sign = 1 # 1 for positive, -1 for negative
        num = 0
        stack = []
        
        for char in s:
            if char.isdigit():
                num = num * 10 + int(char)
            elif char == '+':
                res += sign * num
                sign = 1
                num = 0
            elif char == '-':
                res += sign * num
                sign = -1
                num = 0
            elif char == '(':
                # Push current result and sign onto stack
                stack.append(res)
                stack.append(sign)
                
                # Reset
                res = 0
                sign = 1
            elif char == ')':
                # Finish current expression
                res += sign * num
                num = 0
                
                # Pop context
                prev_sign = stack.pop()
                prev_res = stack.pop()
                
                # Combine
                res = prev_res + prev_sign * res
                
        # Final addition
        res += sign * num
        return res
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`1 - (2 + 3)`

1.  `1`. `res=0, sign=1`. `+`. `res+=1*1=1`. `sign=1`.
2.  `-`. `res+=1*0=1`. `sign=-1`.
3.  `(`. Stack: `[1, -1]`. `res=0, sign=1`.
4.  `2`. `+`. `res+=1*2=2`. `sign=1`.
5.  `3`. `)`.
    -   `res+=1*3=5`. (Inner: 2+3=5).
    -   `pop sign=-1`. `pop val=1`.
    -   `res = 1 + (-1 * 5) = -4`.

Result: -4.
