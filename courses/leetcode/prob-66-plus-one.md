---
layout: page
title: "66. Plus One"
permalink: /courses/leetcode/prob-66-plus-one/
---

# 66. Plus One

## 1. The Question
You are given a large integer represented as an integer array `digits`, where each `digits[i]` is the `i`th digit of the integer. The digits are ordered from most significant to least significant in left-to-right order. The large integer does not contain any leading `0`'s.

Increment the large integer by one and return the resulting array of digits.

### Example 1
**Input**: `digits = [1,2,3]`
**Output**: `[1,2,4]`

### Example 2
**Input**: `digits = [9]`
**Output**: `[1,0]`

---

## 2. Explanation
Iterate from the last digit.
-   Add 1.
-   If sum < 10, we are done. Return result.
-   If sum == 10, set digit to 0, carry continues to next left digit.
-   If we finish the loop (carry propagates past MSB), prepend `1`.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$ (in-place) or $O(N)$ for result if immutable.

---

## 3. Pseudo Code
```text
n = len(digits)
for i in range(n-1, -1, -1):
    if digits[i] < 9:
        digits[i] += 1
        return digits
    digits[i] = 0

# If here, it means we had [9,9,9] -> [0,0,0]
return [1] + digits
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def plusOne(self, digits: list[int]) -> list[int]:
        n = len(digits)
        
        # Iterate from the end
        for i in range(n - 1, -1, -1):
            if digits[i] < 9:
                digits[i] += 1
                return digits
            
            # If digit is 9, it becomes 0 and we continue to carry
            digits[i] = 0
            
        # If we exited the loop, it means we had all 9s (e.g., 999 -> 000)
        # We need to prepend 1
        return [1] + digits
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$ (ignoring output space).

## 6. Example Walkthrough
`[1, 2, 9]`
1.  `i=2`. `digits[2]=9`. Set to `0`. `[1, 2, 0]`.
2.  `i=1`. `digits[1]=2`. `< 9`. Set to `3`. `[1, 3, 0]`.
3.  Return `[1, 3, 0]`.
