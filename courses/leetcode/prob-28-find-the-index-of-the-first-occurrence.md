---
layout: page
title: "28. Find the Index of the First Occurrence in a String"
permalink: /courses/leetcode/prob-28-find-index-of-first-occurrence/
---

# 28. Find the Index of the First Occurrence in a String

## 1. The Question
Given two strings `needle` and `haystack`, return the index of the first occurrence of `needle` in `haystack`, or `-1` if `needle` is not part of `haystack`.

### Example 1
**Input**: `haystack = "sadbutsad", needle = "sad"`
**Output**: `0`
**Explanation**: "sad" occurs at index 0 and 6. The first occurrence is at index 0, so we return 0.

### Example 2
**Input**: `haystack = "leetcode", needle = "leeto"`
**Output**: `-1`
**Explanation**: "leeto" did not occur in "leetcode", so we return -1.

---

## 2. Explanation
This is the classic **substring search** problem.

### Approach 1: Sliding Window / Brute Force
Iterate through `haystack` from `i = 0` to `n - m`.
Check if `haystack[i : i+m] == needle`.
-   **Time**: $O(N \cdot M)$ worst case.
-   **Space**: $O(1)$.

### Approach 2: Built-in Functions
In Python, `haystack.find(needle)` or `haystack.index(needle)` works efficiently (often implemented in C).

### Approach 3: KMP (Knuth-Morris-Pratt) Algorithm (Advanced)
If $N$ and $M$ are huge, we want $O(N+M)$. KMP essentially avoids re-scanning characters in `haystack` by building a "Longest Prefix Suffix" (LPS) array for the `needle`.
However, for interview purposes, usually Sliding Window is sufficient unless $N$ is massive. KMP is good for "Hard" follow-ups.

---

## 3. Pseudo Code (Sliding Window)
```text
n = len(haystack)
m = len(needle)

For i from 0 to n - m:
    # Check substring match
    match = True
    For j from 0 to m - 1:
        If haystack[i+j] != needle[j]:
            match = False
            Break
    
    If match is True: Return i

Return -1
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        if not needle:
            return 0
            
        n = len(haystack)
        m = len(needle)
        
        # We only need to iterate until there are enough characters left
        for i in range(n - m + 1):
            # Check slice equal
            # Note: Slicing in Python creates a new string - O(M)
            # Total complexity O(N*M)
            if haystack[i : i+m] == needle:
                return i
                
        return -1
```

---

## 5. Complexity
-   **Time**: $O((N-M) \cdot M)$, effectively $O(N \cdot M)$.
-   **Space**: $O(1)$ if doing character-by-character comparison, or $O(M)$ if creating slices.

## 6. Example Walkthrough
`haystack = "hello"`, `needle = "ll"`

1.  `i=0`: "he" != "ll"
2.  `i=1`: "el" != "ll"
3.  `i=2`: "ll" == "ll". Return 2.
