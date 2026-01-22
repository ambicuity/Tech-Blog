---
layout: page
title: "383. Ransom Note"
permalink: /courses/leetcode/prob-383-ransom-note/
---

# 383. Ransom Note

## 1. The Question
Given two strings `ransomNote` and `magazine`, return `true` if `ransomNote` can be constructed by using the letters from `magazine` and `false` otherwise.

Each letter in `magazine` can only be used once in `ransomNote`.

### Example 1
**Input**: `ransomNote = "a", magazine = "b"`
**Output**: `false`

### Example 2
**Input**: `ransomNote = "aa", magazine = "ab"`
**Output**: `false`

### Example 3
**Input**: `ransomNote = "aa", magazine = "aab"`
**Output**: `true`

---

## 2. Explanation
We need to check if we have enough "supply" (letters in magazine) to meet the "demand" (letters in ransomNote).

### Approach: Frequency Map (Hash Map)
1.  Count frequency of each char in `magazine`.
2.  Iterate through `ransomNote`. For each char, check if count in map > 0.
3.  Decrement count. If count becomes negative, return `False`.

-   **Time**: $O(M + N)$ where M is length of magazine, N is length of note.
-   **Space**: $O(1)$ (since alphabet size is 26).

---

## 3. Pseudo Code
```text
counts = Counter(magazine)

For char in ransomNote:
    If counts[char] <= 0:
        Return False
    counts[char]--

Return True
```

---

## 4. Optimal Code (Python)

```python
from collections import Counter

class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        # Frequency of available letters
        available = Counter(magazine)
        
        for char in ransomNote:
            if available[char] <= 0:
                return False
            available[char] -= 1
            
        return True
```

---

## 5. Complexity
-   **Time**: $O(M + N)$.
-   **Space**: $O(1)$ (26 chars).

## 6. Example Walkthrough
`note = "aa"`, `mag = "aab"`

1.  `available = {'a': 2, 'b': 1}`.
2.  `char = 'a'`. `avail['a']` is 2. Decrement to 1.
3.  `char = 'a'`. `avail['a']` is 1. Decrement to 0.
4.  End of loop. Return `True`.
