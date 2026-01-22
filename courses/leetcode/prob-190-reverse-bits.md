---
layout: page
title: "190. Reverse Bits"
permalink: /courses/leetcode/prob-190-reverse-bits/
---

# 190. Reverse Bits

## 1. The Question
Reverse bits of a given 32 bits unsigned integer.

### Example 1
**Input**: `n = 00000010100101000001111010011100`
**Output**: `964176192` (`00111001011110000010100101000000`)

---

## 2. Explanation
We need to reverse the 32 bits.
Iterate 0 to 31.
for `i`-th bit of `n`:
-   Extract it: `(n >> i) & 1`.
-   Place it at `31 - i`: `bit << (31 - i)`.
-   OR it into result `res`.

Or simpler loop:
-   `res = (res << 1) | (n & 1)`
-   `n >>= 1`
-   Repeat 32 times.

-   **Time**: $O(1)$ (always 32 bits).
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
res = 0
for _ in range(32):
    res = (res << 1) | (n & 1)
    n >>= 1
return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def reverseBits(self, n: int) -> int:
        result = 0
        for _ in range(32):
            # Shift result to left to make room for new bit
            result = (result << 1)
            
            # Get the last bit of n
            bit = n & 1
            
            # Add the bit to result
            result = result | bit
            
            # Shift n to right to process next bit
            n >>= 1
            
        return result
```

---

## 5. Complexity
-   **Time**: $O(1)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`n=...011` (3 decimal).
1.  `res=0`. `bit=1`. `res=1`. `n=...01`.
2.  `res=10` (2). `bit=1`. `res=11` (3). `n=...0`.
...
32. Final reversed value.
