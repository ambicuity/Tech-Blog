---
layout: page
title: "DSA Ch.15: Dynamic Programming"
permalink: /courses/dsa/ch15-dynamic-programming/
---

# Chapter 15: Dynamic Programming

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 15

## 15.1 Rod Cutting Problem
Given rod of length $n$ and prices $p_i$, maximize revenue.

```python
# Bottom-Up Approach
def rod_cutting(prices, n):
    r = [0] * (n + 1)
    
    for j in range(1, n + 1):
        q = float('-inf')
        for i in range(1, j + 1):
            # Price of cut i + Value of remainder j-i
            q = max(q, prices[i-1] + r[j-i])
        r[j] = q
        
    return r[n]

prices = [1, 5, 8, 9, 10, 17, 17, 20]
print(rod_cutting(prices, 8)) # 22 (Cut into 2 and 6: 5 + 17)
```

## 15.2 Longest Common Subsequence (LCS)
Variables: `X` (len m), `Y` (len n).
Table `c[m+1][n+1]`.

```python
def lcs(X, Y):
    m = len(X)
    n = len(Y)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                
    return dp[m][n]

print(lcs("ABCBDAB", "BDCABA")) # 4 (BCBA)
```
