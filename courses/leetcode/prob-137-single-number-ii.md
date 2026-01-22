---
layout: page
title: "137. Single Number II"
permalink: /courses/leetcode/prob-137-single-number-ii/
---

# 137. Single Number II

## 1. The Question
Given an integer array `nums` where every element appears **three times** except for one, which appears **exactly once**. Find the single element and return it.

You must implement a solution with a linear runtime complexity and use only constant extra space.

### Example 1
**Input**: `nums = [2,2,3,2]`
**Output**: `3`

---

## 2. Explanation
We need to count bits.
For each bit position `i` (0 to 31):
-   Count how many numbers have bit `i` set.
-   If `count % 3 == 0`, the single number has bit `i` unset.
-   If `count % 3 == 1`, the single number has bit `i` set.

Or optimized digital logic:
Maintain "seen once" (`ones`) and "seen twice" (`twos`).
-   `ones = (ones ^ num) & ~twos`
-   `twos = (twos ^ num) & ~ones`

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
ones = 0
twos = 0
for num in nums:
    ones = (ones ^ num) & ~twos
    twos = (twos ^ num) & ~ones
return ones
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        # seen_once: bits that have usually appeared 1st time
        # seen_twice: bits that have appeared 2nd time
        
        seen_once = 0
        seen_twice = 0
        
        for num in nums:
            # If we add num to seen_once:
            # 1. If currently in seen_twice, should not be in seen_once (becomes 3rd time -> 0)
            seen_once = (seen_once ^ num) & (~seen_twice)
            
            # If we add num to seen_twice:
            # 1. If currently in seen_once, moving to seen_twice.
            # 2. But we just updated seen_once (removed if it was there), so we check new seen_once.
            # Wait, standard formula:
            seen_twice = (seen_twice ^ num) & (~seen_once)
            
        return seen_once
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[2, 2, 2, 3]`
1.  `2` (0010). `one=0010`, `two=0000`.
2.  `2` (0010).
    -   `one = (0010 ^ 0010) & ~0 = 0`.
    -   `two = (0000 ^ 0010) & ~0 = 0010`.
3.  `2`.
    -   `one = (0 ^ 2) & ~2 = 0`.
    -   `two = (2 ^ 2) & ~0 = 0`.
    -   Reset both to 0 (appeared 3 times).
4.  `3`. `one=3`, `two=0`.
Result: 3.
