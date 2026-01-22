---
layout: page
title: "392. Is Subsequence"
permalink: /courses/leetcode/prob-392-is-subsequence/
---

# 392. Is Subsequence

## 1. The Question
Given two strings `s` and `t`, return `true` if `s` is a **subsequence** of `t`, or `false` otherwise.

A **subsequence** of a string is a new string that is formed from the original string by deleting some (can be none) of the characters without disturbing the relative positions of the remaining characters. (i.e., `"ace"` is a subsequence of `"abcde"` while `"aec"` is not).

### Example 1
**Input**: `s = "abc", t = "ahbgdc"`
**Output**: `true`

### Example 2
**Input**: `s = "axc", t = "ahbgdc"`
**Output**: `false`

---

## 2. Explanation
We need to check if all characters of `s` appear in `t` in the correct order.

### Approach: Two Pointers
1.  Pointer `i` for `s`, Pointer `j` for `t`.
2.  Iterate through `t` using `j`.
3.  If `t[j] == s[i]`, it means we found the current character of `s`. Move `i` forward.
4.  Always move `j` forward.
5.  If `i` reaches the end of `s`, we found everything.

-   **Time**: $O(T)$ where $T$ is diff length of `t`.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
i = 0, j = 0
While i < len(s) AND j < len(t):
    If s[i] == t[j]:
        i++
    j++

Return i == len(s)
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def isSubsequence(self, s: str, t: str) -> bool:
        if not s:
            return True
            
        i, j = 0, 0
        n, m = len(s), len(t)
        
        while i < n and j < m:
            # If characters match, move s-pointer
            if s[i] == t[j]:
                i += 1
            # Always move t-pointer
            j += 1
            
        return i == n
```

---

## 5. Complexity
-   **Time**: $O(T)$ where T is length of `t`.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`s="abc"`, `t="ahbgdc"`

1.  `s[0]='a'`, `t[0]='a'`. Match. `i=1` ('b'), `j=1`.
2.  `s[1]='b'`, `t[1]='h'`. No match. `j=2`.
3.  `s[1]='b'`, `t[2]='b'`. Match. `i=2` ('c'), `j=3`.
4.  `s[2]='c'`, `t[3]='g'`. No match. `j=4`.
5.  `s[2]='c'`, `t[4]='d'`. No match. `j=5`.
6.  `s[2]='c'`, `t[5]='c'`. Match. `i=3`.
Loop ends as `i == len(s)`. Return True.
