---
layout: page
title: "76. Minimum Window Substring"
permalink: /courses/leetcode/prob-76-minimum-window-substring/
---

# 76. Minimum Window Substring

## 1. The Question
Given two strings `s` and `t`, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window. If there is no such substring, return the empty string `""`.

### Example 1
**Input**: `s = "ADOBECODEBANC", t = "ABC"`
**Output**: `"BANC"`

---

## 2. Explanation
**Sliding Window**.
1.  Count frequency of chars in `t`. `target_counts`.
2.  Expand `right` pointer. Add `s[right]` to `window_counts`.
3.  Check if window is valid (formed). (Maintain a `formed` variable: number of unique chars that meet the requirement).
4.  If valid, try to shrink from `left` to minimize.
    -   Update min_len.
    -   Remove `s[left]`. Update `window_counts` and `formed`.
    -   `left++`.

-   **Time**: $O(S + T)$.
-   **Space**: $O(1)$ (bounded by char set size).

---

## 3. Pseudo Code
```text
need = Counter(t), have = Counter()
n_need = len(need), n_have = 0
l = 0, res = ""

for r in range(len(s)):
    c = s[r]
    have[c] += 1
    if have[c] == need[c]: n_have += 1
    
    while n_have == n_need:
        update_result(s[l:r+1])
        rem = s[l]
        have[rem] -= 1
        if have[rem] < need[rem]: n_have -= 1
        l += 1
return res
```

---

## 4. Optimal Code (Python)

```python
from collections import Counter

class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if not t or not s:
            return ""
            
        dict_t = Counter(t)
        required = len(dict_t)
        
        # Filter s? No, just iterate.
        l, r = 0, 0
        formed = 0
        window_counts = {}
        
        ans = float("inf"), None, None # len, left, right
        
        while r < len(s):
            char = s[r]
            window_counts[char] = window_counts.get(char, 0) + 1
            
            if char in dict_t and window_counts[char] == dict_t[char]:
                formed += 1
                
            while l <= r and formed == required:
                char = s[l]
                
                # Save the smallest window until now.
                if r - l + 1 < ans[0]:
                    ans = (r - l + 1, l, r)
                    
                window_counts[char] -= 1
                if char in dict_t and window_counts[char] < dict_t[char]:
                    formed -= 1
                
                l += 1    
            
            r += 1
            
        return "" if ans[0] == float("inf") else s[ans[1] : ans[2] + 1]
```

---

## 5. Complexity
-   **Time**: $O(|S| + |T|)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`ADOBECODEBANC`, `ABC`.
... Finds `BANC`.
