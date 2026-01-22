---
layout: page
title: "172. Factorial Trailing Zeroes"
permalink: /courses/leetcode/prob-172-factorial-trailing-zeroes/
---

# 172. Factorial Trailing Zeroes

## 1. The Question
Given an integer `n`, return the number of trailing zeroes in `n!`.

Note that `n! = n * (n - 1) * ... * 2 * 1`.

### Example 1
**Input**: `n = 3`
**Output**: `0`
**Explanation**: `3! = 6`, no trailing zero.

### Example 2
**Input**: `n = 5`
**Output**: `1`
**Explanation**: `5! = 120`, one trailing zero.

---

## 2. Explanation
Trailing zeroes are produced by factors of `10`, which is `2 * 5`.
In `1` to `n`, there are plenty of factors of `2` (every even number).
The limiting factor is the count of factor `5`.
So we simply count how many "5"s are in the factorization of `n!`.
Factors of 5: 5, 10, 15, 20, 25...
-   Multiples of 5 contribute one `5`.
-   Multiples of 25 contribute **two** `5`s (one is counted in multiples of 5, one extra).
-   Multiples of 125 contribute **three** `5`s.

Algorithm:
Sum `n // 5`, `n // 25`, `n // 125`, etc.

-   **Time**: $O(\log_5 N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
count = 0
while n > 0:
    n //= 5
    count += n
return count
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def trailingZeroes(self, n: int) -> int:
        zero_count = 0
        while n > 0:
            n //= 5
            zero_count += n
        return zero_count
```

---

## 5. Complexity
-   **Time**: $O(\log N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`n = 30`.
1.  `30 // 5 = 6`. Count = 6.
2.  `6 // 5 = 1`. Count = 6 + 1 = 7.
3.  `1 // 5 = 0`. Stop.
Result 7.
(Factors: 5, 10, 15, 20, 25(x2), 30. Total 1+1+1+1+2+1 = 7).
