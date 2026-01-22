---
layout: page
title: "136. Single Number"
permalink: /courses/leetcode/prob-136-single-number/
---

# 136. Single Number

## 1. The Question
Given a **non-empty** array of integers `nums`, every element appears *twice* except for one. Find that single one.

You must implement a solution with a linear runtime complexity and use only constant extra space.

### Example 1
**Input**: `nums = [2,2,1]`
**Output**: `1`

### Example 2
**Input**: `nums = [4,1,2,1,2]`
**Output**: `4`

---

## 2. Explanation
XOR property:
-   `A ^ A = 0`
-   `A ^ 0 = A`
-   `A ^ B ^ A = B` (Commutative).

If we XOR all numbers, pairs will cancel out (`A ^ A = 0`), leaving only the single number.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
res = 0
for x in nums:
    res ^= x
return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        result = 0
        for num in nums:
            result ^= num
        return result
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[4, 1, 2, 1, 2]`
1.  `res=0`.
2.  `^ 4 -> 4`.
3.  `^ 1 -> 5`.
4.  `^ 2 -> 7`.
5.  `^ 1 -> 6`.
6.  `^ 2 -> 4`.
Result: 4.
