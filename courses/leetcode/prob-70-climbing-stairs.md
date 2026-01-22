---
layout: page
title: "70. Climbing Stairs"
permalink: /courses/leetcode/prob-70-climbing-stairs/
---

# 70. Climbing Stairs

## 1. The Question
You are climbing a staircase. It takes `n` steps to reach the top.

Each time you can either climb `1` or `2` steps. In how many distinct ways can you climb to the top?

### Example 1
**Input**: `n = 2`
**Output**: `2`
**Explanation**: Two ways: (1, 1), (2).

### Example 2
**Input**: `n = 3`
**Output**: `3`
**Explanation**: Three ways: (1, 1, 1), (1, 2), (2, 1).

---

## 2. Explanation
Reference relationship:
To reach step `i`, one could have arrived from:
-   Step `i-1` (by taking 1 step).
-   Step `i-2` (by taking 2 steps).

So `ways[i] = ways[i-1] + ways[i-2]`.
Base cases:
-   `ways[1] = 1`.
-   `ways[2] = 2`.

This is exactly the **Fibonacci Sequence**.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
if n <= 2: return n
a, b = 1, 2
for _ in range(3, n+1):
    a, b = b, a + b
return b
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def climbStairs(self, n: int) -> int:
        if n <= 2:
            return n
            
        prev2 = 1 # ways to reach step 1
        prev1 = 2 # ways to reach step 2
        
        for i in range(3, n + 1):
            current = prev1 + prev2
            prev2 = prev1
            prev1 = current
            
        return prev1
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`n=4`.
1.  `prev2=1`, `prev1=2`.
2.  `i=3`. `cur = 1+2 = 3`. `p2=2, p1=3`.
3.  `i=4`. `cur = 2+3 = 5`. `p2=3, p1=5`.
Result 5.
Ways: `1111, 112, 121, 211, 22`. Correct.
