---
layout: page
title: "202. Happy Number"
permalink: /courses/leetcode/prob-202-happy-number/
---

# 202. Happy Number

## 1. The Question
Write an algorithm to determine if a number `n` is "happy".

A **happy number** is a number defined by the following process:
1.  Starting with any positive integer, replace the number by the sum of the squares of its digits.
2.  Repeat the process until the number equals 1 (where it will stay), or it loops endlessly in a cycle which does not include 1.
3.  Those numbers for which this process ends in 1 are happy.

Return `true` if `n` is a happy number, and `false` if not.

### Example 1
**Input**: `n = 19`
**Output**: `true`
**Explanation**:
$1^2 + 9^2 = 82$
$8^2 + 2^2 = 68$
$6^2 + 8^2 = 100$
$1^2 + 0^2 + 0^2 = 1$

### Example 2
**Input**: `n = 2`
**Output**: `false`

---

## 2. Explanation
This is essentially a cycle detection problem.
The sequence of numbers generated is like a linked list. We need to detect if it reaches `1` (true) or enters a cycle (false).

### Approach 1: Hash Set
Keep track of all numbers seen.
If we see a number again, it's a cycle -> return False.
If we reach 1 -> return True.

### Approach 2: Floyd's Cycle-Finding Algorithm (Fast/Slow Pointers)
Use two runners: `slow` (1 step) and `fast` (2 steps).
If `slow == fast`, cycle detected.
If `fast == 1`, happy.
-   **Space**: $O(1)$.

We will implement **Approach 1** for simplicity, as the maximum number of iterations is small (sum of squares for integer max is 162).

---

## 3. Pseudo Code
```text
seen = Set()
while n != 1:
    if n in seen:
        Return False
    seen.add(n)
    n = sum_of_squares(n)

Return True
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def isHappy(self, n: int) -> bool:
        seen = set()
        
        while n != 1:
            if n in seen:
                return False
                
            seen.add(n)
            
            # Calculate sum of squares
            sum_sq = 0
            while n > 0:
                digit = n % 10
                sum_sq += digit * digit
                n //= 10
                
            n = sum_sq
            
        return True
```

---

## 5. Complexity
-   **Time**: $O(\log N)$. Finding digits takes log N. Number of steps is bounded (hard to prove, but around 20).
-   **Space**: $O(\log N)$.

## 6. Example Walkthrough
`n = 2`.
1.  $2^2 = 4$. Seen={2}.
2.  $4^2 = 16$. Seen={2,4}.
3.  $1^2 + 6^2 = 37$. Seen={2,4,16}.
4.  $3^2 + 7^2 = 58$.
5.  $5^2 + 8^2 = 89$.
6.  $8^2 + 9^2 = 145$.
7.  $1^2 + 4^2 + 5^2 = 42$.
8.  $4^2 + 2^2 = 20$.
9.  $2^2 + 0^2 = 4$.
10. `4` is in Seen! Cycle. Return `False`.
