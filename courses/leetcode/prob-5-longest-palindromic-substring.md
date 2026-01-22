---
layout: page
title: "5. Longest Palindromic Substring"
permalink: /courses/leetcode/prob-5-longest-palindromic-substring/
---

# 5. Longest Palindromic Substring

## 1. The Question
Given a string `s`, return the longest palindromic substring in `s`.

### Example 1
**Input**: `s = "babad"`
**Output**: `"bab"`
**Explanation**: "aba" is also a valid answer.

### Example 2
**Input**: `s = "cbbd"`
**Output**: `"bb"`

---

## 2. Explanation
Approaches:
1.  **DP**: `dp[i][j]` is true if `s[i:j+1]` is palindrome.
    -   `s[i] == s[j]` AND `dp[i+1][j-1]` is true.
    -   Space $O(N^2)$, Time $O(N^2)$.
2.  **Expand Around Center**:
    -   For each `i`, expand left and right.
    -   Centers can be `i` (odd len) or `i, i+1` (even len).
    -   Space $O(1)$, Time $O(N^2)$.

Expand Around Center is preferred due to space complexity.

-   **Time**: $O(N^2)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
res = ""
for i in 0..n:
    # Odd
    l, r = i, i
    while l>=0 and r<n and s[l]==s[r]:
        if len > max: update
        l--, r++
    
    # Even
    l, r = i, i+1
    while l>=0 and r<n and s[l]==s[r]:
        if len > max: update
        l--, r++
return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def longestPalindrome(self, s: str) -> str:
        res = ""
        res_len = 0
        
        for i in range(len(s)):
            # Odd length
            l, r = i, i
            while l >= 0 and r < len(s) and s[l] == s[r]:
                if (r - l + 1) > res_len:
                    res = s[l:r+1]
                    res_len = r - l + 1
                l -= 1
                r += 1
            
            # Even length
            l, r = i, i + 1
            while l >= 0 and r < len(s) and s[l] == s[r]:
                if (r - l + 1) > res_len:
                    res = s[l:r+1]
                    res_len = r - l + 1
                l -= 1
                r += 1
                
        return res
```

---

## 5. Complexity
-   **Time**: $O(N^2)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`babad`.
1.  `i=0`. Odd `b` (1). Even `ba` (0). Res `b`.
2.  `i=1`. Odd `bab` (3). Even `ab` (0). Res `bab`.
3.  `i=2`. Odd `b` (1). Abs `aba` (3). Even `ba`.
4.  ...
Result `bab`.
