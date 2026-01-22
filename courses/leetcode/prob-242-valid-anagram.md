---
layout: page
title: "242. Valid Anagram"
permalink: /courses/leetcode/prob-242-valid-anagram/
---

# 242. Valid Anagram

## 1. The Question
Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.

An **Anagram** is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.

### Example 1
**Input**: `s = "anagram", t = "nagaram"`
**Output**: `true`

### Example 2
**Input**: `s = "rat", t = "car"`
**Output**: `false`

---

## 2. Explanation
Two strings are anagrams if they have the exact same characters with the exact same frequencies.

### Approach 1: Sorting
Sort both strings and compare.
-   **Time**: $O(N \log N)$.
-   **Space**: $O(1)$ or $O(N)$ depending on sort.

### Approach 2: Frequency Map (Optimal)
1.  Check lengths. If `len(s) != len(t)`, return False.
2.  Count char frequencies in `s` and `t`.
3.  Compare the maps.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$ (26 chars).

---

## 3. Pseudo Code
```text
If len(s) != len(t): Return False

countS = Counter(s)
countT = Counter(t)

Return countS == countT
```

---

## 4. Optimal Code (Python)

```python
from collections import Counter

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
            
        # Python's Counter compares frequency equality
        return Counter(s) == Counter(t)
        
    def isAnagram_manual(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
            
        count = [0] * 26
        
        for char in s:
            count[ord(char) - ord('a')] += 1
            
        for char in t:
            count[ord(char) - ord('a')] -= 1
            if count[ord(char) - ord('a')] < 0:
                return False
                
        return True
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`s="rat", t="car"`

1.  `count['r']++`, `count['a']++`, `count['t']++`.
2.  `t`: `count['c']--`. Negative! Return False.
