---
layout: page
title: "67. Add Binary"
permalink: /courses/leetcode/prob-67-add-binary/
---

# 67. Add Binary

## 1. The Question
Given two binary strings `a` and `b`, return their sum as a binary string.

### Example 1
**Input**: `a = "11", b = "1"`
**Output**: `100`

### Example 2
**Input**: `a = "1010", b = "1011"`
**Output**: `10101`

---

## 2. Explanation
We perform column-by-column addition from right to left, similar to adding decimal numbers.
Maintain a `carry`.
At each position `i`:
`sum = a[i] + b[i] + carry`
`result_bit = sum % 2`
`carry = sum // 2`

-   **Time**: $O(\max(N, M))$.
-   **Space**: $O(\max(N, M))$ for the result string.

---

## 3. Pseudo Code
```text
i = len(a)-1, j = len(b)-1
carry = 0
res = []

while i >= 0 or j >= 0 or carry:
    sum_val = carry
    if i >= 0: sum_val += int(a[i]); i -= 1
    if j >= 0: sum_val += int(b[j]); j -= 1
    
    res.append(str(sum_val % 2))
    carry = sum_val // 2
    
return "".join(res[::-1])
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def addBinary(self, a: str, b: str) -> str:
        i, j = len(a) - 1, len(b) - 1
        carry = 0
        result = []
        
        while i >= 0 or j >= 0 or carry:
            current_sum = carry
            
            if i >= 0:
                current_sum += int(a[i])
                i -= 1
            if j >= 0:
                current_sum += int(b[j])
                j -= 1
                
            # Append the least significant bit
            result.append(str(current_sum % 2))
            
            # Update carry
            carry = current_sum // 2
            
        return "".join(result[::-1])
```

---

## 5. Complexity
-   **Time**: $O(\max(N, M))$.
-   **Space**: $O(\max(N, M))$.

## 6. Example Walkthrough
`a="11", b="1"`
1.  `i=1, j=0, c=0`.
    -   `sum = 0 + 1 + 1 = 2`.
    -   `res = ["0"]`. `c = 1`.
2.  `i=0, j=-1, c=1`.
    -   `sum = 1 + 1 + 0 = 2`.
    -   `res = ["0", "0"]`. `c = 1`.
3.  `i=-1, j=-1, c=1`.
    -   `sum = 1`.
    -   `res = ["0", "0", "1"]`. `c = 0`.
4.  Reverse: `100`.
