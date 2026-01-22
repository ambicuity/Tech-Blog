---
layout: page
title: "201. Bitwise AND of Numbers Range"
permalink: /courses/leetcode/prob-201-bitwise-and-of-numbers-range/
---

# 201. Bitwise AND of Numbers Range

## 1. The Question
Given two integers `left` and `right` that represent the range `[left, right]`, return the bitwise AND of all numbers in this range, inclusive.

### Example 1
**Input**: `left = 5, right = 7`
**Output**: `4`
**Explanation**: `5 & 6 & 7`.
`101 & 110 & 111`.
Result `100` (4).

### Example 2
**Input**: `left = 0, right = 0`
**Output**: `0`

---

## 2. Explanation
The AND of a range is just the **common prefix** of `left` and `right`.
Any bit that flips between `left` and `right` (and all lower bits) will eventually be 0 in the result.
Why? Because going from `left` to `right` involves passing through a number where that bit flips from 0 to 1, or 1 to 0. If it flips, there's at least one `0` in that column in the range. ANDing with 0 makes it 0.

So we just need to find the common high-order bits.

-   **Time**: $O(32)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
shift = 0
while left < right:
    left >>= 1
    right >>= 1
    shift += 1
return left << shift
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def rangeBitwiseAnd(self, left: int, right: int) -> int:
        shift = 0
        # Find the common prefix
        while left < right:
            left >>= 1
            right >>= 1
            shift += 1
            
        return left << shift
```

---

## 5. Complexity
-   **Time**: $O(1)$ (log Right).
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`left=5 (101), right=7 (111)`
1.  `5 < 7`. Shift 1. `l=2 (10), r=3 (11)`. `s=1`.
2.  `2 < 3`. Shift 1. `l=1 (1), r=1 (1)`. `s=2`.
3.  `1 == 1`. Stop.
Result: `1 << 2 = 100` (4).
