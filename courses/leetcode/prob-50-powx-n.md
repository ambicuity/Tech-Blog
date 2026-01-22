---
layout: page
title: "50. Pow(x, n)"
permalink: /courses/leetcode/prob-50-powx-n/
---

# 50. Pow(x, n)

## 1. The Question
Implement `pow(x, n)`, which calculates `x` raised to the power `n` (i.e., `x^n`).

### Example 1
**Input**: `x = 2.00000, n = 10`
**Output**: `1024.00000`

### Example 2
**Input**: `x = 2.00000, n = -2`
**Output**: `0.25000`

---

## 2. Explanation
Naive iteration $O(N)$ is too slow if $N$ is large (e.g., $2^{31}-1$).
Use **Binary Exponentiation** (Divide & Conquer).
$x^n = (x^2)^{n/2}$ if $n$ is even.
$x^n = x \cdot (x^2)^{(n-1)/2}$ if $n$ is odd.

Handle negative `n`: $x^{-n} = 1 / x^n$.
Or just `x = 1/x`, `n = -n`.

-   **Time**: $O(\log N)$.
-   **Space**: $O(\log N)$ recursive or $O(1)$ iterative.

---

## 3. Pseudo Code
```text
if n < 0: x = 1/x, n = -n
res = 1
curr = x
while n > 0:
    if n % 2 == 1:
        res *= curr
    curr *= curr
    n //= 2
return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def myPow(self, x: float, n: int) -> float:
        if n == 0:
            return 1.0
        
        if n < 0:
            x = 1 / x
            n = -n
            
        result = 1
        current_product = x
        
        while n > 0:
            if n % 2 == 1:
                result *= current_product
                
            current_product *= current_product
            n //= 2
            
        return result
```

---

## 5. Complexity
-   **Time**: $O(\log n)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`2.0, 10`.
1.  `n=10`. `res=1`. `curr=2`.
2.  `n=5`. `curr=4`.
3.  `5%2==1`. `res=1*4=4`. `curr=16`.
4.  `n=2`. `curr=256`.
5.  `n=1`. `curr=65536`. (Wait, let's retrace logic).

Correction:
1.  `n=10`. `curr=2`.
2.  Even. `curr=4`, `n=5`.
3.  Odd. `res=4`. `curr=16`, `n=2`.
4.  Even. `curr=256`, `n=1`.
5.  Odd. `res=4*256=1024`. `curr=...`, `n=0`.
Stop. 1024.
