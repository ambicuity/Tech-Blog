---
layout: page
title: "9. Palindrome Number"
permalink: /courses/leetcode/prob-9-palindrome-number/
---

# 9. Palindrome Number

## 1. The Question
Given an integer `x`, return `true` if `x` is a palindrome integer.

An integer is a **palindrome** when it reads the same backward as forward.
-   For example, `121` is a palindrome while `123` is not.

### Example 1
**Input**: `x = 121`
**Output**: `true`

### Example 2
**Input**: `x = -121`
**Output**: `false`
**Explanation**: From left to right, it reads -121. From right to left, it becomes 121-. Therefore it is not a palindrome.

---

## 2. Explanation
1.  Negative numbers are not palindromes.
2.  Multiply/Revert number approach:
    -   Store copy of `x`.
    -   Reverse `x` mathematically (`rev = rev * 10 + x % 10`).
    -   Compare `rev` with original.
3.  Optimization: Revert only **half** of the number to avoid potential overflow (in fixed-integer languages).
    -   Stop when `rev >= x`.

-   **Time**: $O(\log_{10} x)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
if x < 0: return False
original = x
rev = 0
while x > 0:
    rev = rev * 10 + x % 10
    x //= 10
return original == rev
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def isPalindrome(self, x: int) -> bool:
        # Negative numbers are not palindromes
        # Also numbers ending in 0 (except 0 itself) are not palindromes (e.g., 10 -> 01)
        if x < 0 or (x % 10 == 0 and x != 0):
            return False
            
        reverted_number = 0
        original = x
        
        # Simple full reversal (Python handles large integers automatically)
        while x > 0:
            reverted_number = reverted_number * 10 + x % 10
            x //= 10
            
        return original == reverted_number
```

---

## 5. Complexity
-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`121`
1.  `rev=0, x=121`.
2.  `rev=1, x=12`.
3.  `rev=12, x=1`.
4.  `rev=121, x=0`.
`121 == 121`. True.
