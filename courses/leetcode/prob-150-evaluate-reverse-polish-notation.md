---
layout: page
title: "150. Evaluate Reverse Polish Notation"
permalink: /courses/leetcode/prob-150-evaluate-reverse-polish-notation/
---

# 150. Evaluate Reverse Polish Notation

## 1. The Question
Evaluate the value of an arithmetic expression in **Reverse Polish Notation** (RPN).

Valid operators are `+`, `-`, `*`, and `/`. Each operand may be an integer or another expression.

**Note**:
-   Division between two integers should truncate toward zero.
-   The given RPN expression is always valid. This means the expression would always evaluate to a result, and there will not be any division by zero operation.

### Example 1
**Input**: `tokens = ["2","1","+","3","*"]`
**Output**: `9`
**Explanation**: `((2 + 1) * 3) = 9`

### Example 2
**Input**: `tokens = ["4","13","5","/","+"]`
**Output**: `6`
**Explanation**: `(4 + (13 / 5)) = 6`

### Example 3
**Input**: `tokens = ["10","6","9","3","+","-11","*","/","*","17","+","5","+"]`
**Output**: `22`
**Explanation**:
((10 * (6 / ((9 + 3) * -11))) + 17) + 5
= ((10 * (6 / (12 * -11))) + 17) + 5
= ((10 * (6 / -132)) + 17) + 5
= ((10 * 0) + 17) + 5
= (0 + 17) + 5
= 17 + 5
= 22

---

## 2. Explanation
RPN is a postfix notation. `A B +` means `A + B`.
This naturally fits a **Stack**.
-   If token is number: Push to stack.
-   If token is operator: Pop two numbers `b` and `a`, perform `a op b`, push result.
    -   Note order: `b` is popped first (top), `a` second. Operation is `a - b` or `a / b`.

Special case for division in Python: `int(a / b)` truncates towards zero (like C/Java integer division), while `a // b` floors (rounds down). e.g., `-1 / 10`. Integer division `0`. Floor division `-1`. We must use `int(a / b)`.

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
stack = []
For t in tokens:
    if t is number:
        stack.push(int(t))
    else:
        b = stack.pop()
        a = stack.pop()
        if t == '+': push(a+b)
        if t == '-': push(a-b)
        if t == '*': push(a*b)
        if t == '/': push(int(a/b))

Return stack[0]
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def evalRPN(self, tokens: list[str]) -> int:
        stack = []
        
        for token in tokens:
            if token not in "+-*/":
                stack.append(int(token))
            else:
                b = stack.pop()
                a = stack.pop()
                
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    # Note: Python's // is floor division.
                    # int(a / b) is truncation towards zero.
                    # e.g., int(6 / -132) -> 0. 6 // -132 -> -1.
                    stack.append(int(a / b))
                    
        return stack[0]
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`["4", "13", "5", "/", "+"]`

1.  Push `4`: `[4]`
2.  Push `13`: `[4, 13]`
3.  Push `5`: `[4, 13, 5]`
4.  Op `/`. `b=5, a=13`. `13 / 5 = 2.6 -> 2`. Push `2`. Stack: `[4, 2]`
5.  Op `+`. `b=2, a=4`. `4 + 2 = 6`. Push `6`. Stack: `[6]`.

Result: 6.
