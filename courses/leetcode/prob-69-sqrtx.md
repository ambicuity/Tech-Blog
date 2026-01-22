---
layout: page
title: "69. Sqrt(x)"
permalink: /courses/leetcode/prob-69-sqrtx/
---

# 69. Sqrt(x)

## 1. The Question
Given a non-negative integer `x`, return the square root of `x` rounded down to the nearest integer. The returned integer should be non-negative as well.

You must not use any built-in exponent function or operator.

### Example 1
**Input**: `x = 4`
**Output**: `2`

### Example 2
**Input**: `x = 8`
**Output**: `2`

---

## 2. Explanation
Find integer `k` such that `k*k <= x` and `(k+1)*(k+1) > x`.
Binary Search between `0` and `x`.
-   If `mid*mid == x`: return `mid`.
-   If `mid*mid < x`: `ans = mid` (potential answer), look right (`l = mid + 1`).
-   If `mid*mid > x`: look left (`r = mid - 1`).

-   **Time**: $O(\log x)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
l, r = 0, x
ans = 0

while l <= r:
    mid = (l+r)//2
    if mid*mid == x: return mid
    elif mid*mid < x:
        ans = mid
        l = mid + 1
    else:
        r = mid - 1
return ans
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def mySqrt(self, x: int) -> int:
        if x == 0:
            return 0
            
        left, right = 1, x
        ans = 0
        
        while left <= right:
            mid = (left + right) // 2
            
            if mid * mid <= x:
                ans = mid
                left = mid + 1
            else:
                right = mid - 1
                
        return ans
```

---

## 5. Complexity
-   **Time**: $O(\log x)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`x=8`.
1.  `1, 8`. Mid 4. `16 > 8`. `r=3`.
2.  `1, 3`. Mid 2. `4 <= 8`. `ans=2, l=3`.
3.  `3, 3`. Mid 3. `9 > 8`. `r=2`.
4.  `3, 2`. Stop. Return 2.
