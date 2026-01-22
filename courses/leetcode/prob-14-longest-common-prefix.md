---
layout: page
title: "14. Longest Common Prefix"
permalink: /courses/leetcode/prob-14-longest-common-prefix/
---

# 14. Longest Common Prefix

## 1. The Question
Write a function to find the longest common prefix string amongst an array of strings.

If there is no common prefix, return an empty string `""`.

### Example 1
**Input**: `strs = ["flower","flow","flight"]`
**Output**: `"fl"`

### Example 2
**Input**: `strs = ["dog","racecar","car"]`
**Output**: `""`
**Explanation**: There is no common prefix among the input strings.

---

## 2. Explanation
We need to find the string part that is identical at the start of **all** strings.

### Approach 1: Horizontal Scanning
Take the first string as the `prefix`. Compare it with the second. Update `prefix` to be the common part. Compare new `prefix` with the third, and so on.

### Approach 2: Vertical Scanning
Look at the first character of all strings. If they match, append to result.
Look at the second character of all strings. If match, append.
Stop if mismatch or if we reach the end of the shortest string.

### Approach 3: Sorting (Optimal for code simplicity)
Sort the array of strings. The longest common prefix must be a prefix of the **first** and the **last** string (because sorting groups similar prefixes).
So we just compare `strs[0]` and `strs[-1]`.

-   **Time**: $O(S \log n)$ where S is sum of characters for sorting. Or $O(n \cdot m)$ for scanning.
-   **Space**: $O(1)$ extra space.

---

## 3. Pseudo Code (Sorting Approach)
```text
If strs is empty: return ""

Sort strs
s1 = strs[0]
s2 = strs[-1]
idx = 0

While idx < length(s1) AND idx < length(s2):
    If s1[idx] == s2[idx]:
        idx++
    Else:
        Break

Return s1[0...idx]
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def longestCommonPrefix(self, strs: list[str]) -> str:
        if not strs:
            return ""
            
        # Approach: Sorting
        # The common prefix must be present in the "smallest" and "largest" string (lexicographically)
        strs.sort()
        
        first = strs[0]
        last = strs[-1]
        
        i = 0
        min_len = min(len(first), len(last))
        
        while i < min_len and first[i] == last[i]:
            i += 1
            
        return first[:i]
```

---

## 5. Complexity
-   **Time**: $O(N \log N \cdot M)$ due to sorting (where N is array length, M is string length).
-   **Space**: $O(1)$ or $O(M)$ for sorting depending on implementation.

## 6. Example Walkthrough
`strs = ["flower", "flow", "flight"]`

1.  Sort: `["flight", "flow", "flower"]`
2.  Compare `first="flight"` vs `last="flower"`.
3.  `i=0`: `f == f` -> OK.
4.  `i=1`: `l == l` -> OK.
5.  `i=2`: `i != o` -> Stop.
6.  Return `first[:2]` -> `"fl"`.
