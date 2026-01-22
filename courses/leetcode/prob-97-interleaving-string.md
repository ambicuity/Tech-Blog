---
layout: page
title: "97. Interleaving String"
permalink: /courses/leetcode/prob-97-interleaving-string/
---

# 97. Interleaving String

## 1. The Question
Given strings `s1`, `s2`, and `s3`, find whether `s3` is formed by an **interleaving** of `s1` and `s2`.

An interleaving of two strings `s` and `t` is a configuration where `s` and `t` are divided into `n` and `m` substrings respectively, such that:
-   `s = s1 + s2 + ... + sn`
-   `t = t1 + t2 + ... + tm`
-   The interleaving is `s1 + t1 + s2 + t2 + ...` or `t1 + s1 + t2 + s2 + ...`

Essentially, `s3` maintains the relative order of characters from `s1` and `s2`.

### Example 1
**Input**: `s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac"`
**Output**: `true`

---

## 2. Explanation
DP State: `dp[i][j]` = true if `s1[0..i]` and `s2[0..j]` can interleave to form `s3[0..i+j]`.
Transition:
`dp[i][j]` is True if:
1.  (`s1[i-1] == s3[i+j-1]` AND `dp[i-1][j]` is True)
    OR
2.  (`s2[j-1] == s3[i+j-1]` AND `dp[i][j-1]` is True)

Base case: `dp[0][0] = True`.

-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(M \cdot N)$ or $O(N)$ optimized.

---

## 3. Pseudo Code
```text
if len(s1) + len(s2) != len(s3): return False
dp = Matrix (m+1)x(n+1)
dp[0][0] = True

for i in 0..m:
    for j in 0..n:
        if i>0 and s1[i-1]==s3[i+j-1] and dp[i-1][j]: dp[i][j]=True
        if j>0 and s2[j-1]==s3[i+j-1] and dp[i][j-1]: dp[i][j]=True
return dp[m][n]
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def isInterleave(self, s1: str, s2: str, s3: str) -> bool:
        if len(s1) + len(s2) != len(s3):
            return False
            
        # Optimize space to O(N) using 1D DP
        # dp[j] implies dp[i][j] (current row)
        n = len(s2)
        dp = [False] * (n + 1)
        
        for i in range(len(s1) + 1):
            for j in range(len(s2) + 1):
                if i == 0 and j == 0:
                    dp[j] = True
                elif i == 0:
                    # Only s2 matters
                    dp[j] = dp[j-1] and s2[j-1] == s3[i+j-1]
                elif j == 0:
                    # Only s1 matters
                    # dp[j] corresponds to dp[i-1][0] (value from prev row)
                    dp[j] = dp[j] and s1[i-1] == s3[i+j-1]
                else:
                    # dp[j] comes from dp[i-1][j] (previous row, same col) -> check s1
                    # dp[j-1] comes from dp[i][j-1] (current row, prev col) -> check s2
                    match_s1 = dp[j] and s1[i-1] == s3[i+j-1]
                    match_s2 = dp[j-1] and s2[j-1] == s3[i+j-1]
                    dp[j] = match_s1 or match_s2
                    
        return dp[n]
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`s1="a", s2="b", s3="ab"`
1.  `i=0, j=0`. `dp[0]=T`.
2.  `i=0, j=1`. `dp[1] = dp[0] & (b==a)` -> F. (s3[0] is 'a').
3.  `i=1, j=0`. `dp[0] = dp[0] & (a==a)` -> T.
4.  `i=1, j=1`. `dp[1] = (dp[1] & a==b) | (dp[0] & b==b)`.
    -   `dp[1]` was F.
    -   `dp[0]` is T. `b==b` is T. `s3[1]` is 'b'.
    -   Result T.
True.
