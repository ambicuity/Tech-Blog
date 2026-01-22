---
layout: page
title: "191. Number of 1 Bits"
permalink: /courses/leetcode/prob-191-number-of-1-bits/
---

# 191. Number of 1 Bits

## 1. The Question
Write a function that takes the binary representation of a positive integer and returns the number of set bits (also known as the Hamming weight).

### Example 1
**Input**: `n = 11` (`1011`)
**Output**: `3`

---

## 2. Explanation
Count the number of '1's.
Method 1: Loop 32 times, check `n & 1`.
Method 2: Brian Kernighan’s Algorithm.
`n & (n - 1)` flips the **least significant set bit** to 0.
Repeat until `n` becomes 0. The number of iterations is the number of set bits.

-   **Time**: $O(1)$ (max 32 ops). Best case $O(k)$ where k is set bits.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
count = 0
while n:
    n = n & (n - 1)
    count += 1
return count
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def hammingWeight(self, n: int) -> int:
        count = 0
        while n:
            n &= (n - 1)
            count += 1
        return count
```

---

## 5. Complexity
-   **Time**: $O(1)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`n=11` (1011).
1.  `1011 & 1010 = 1010`. Count=1.
2.  `1010 & 1001 = 1000`. Count=2.
3.  `1000 & 0111 = 0000`. Count=3.
Return 3.
