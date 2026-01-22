---
layout: page
title: "58. Length of Last Word"
permalink: /courses/leetcode/prob-58-length-of-last-word/
---

# 58. Length of Last Word

## 1. The Question
Given a string `s` consisting of words and spaces, return the length of the **last** word in the string.

A **word** is a maximal substring consisting of non-space characters only.

### Example 1
**Input**: `s = "Hello World"`
**Output**: `5`
**Explanation**: The last word is "World" with length 5.

### Example 2
**Input**: `s = "   fly me   to   the moon  "`
**Output**: `4`
**Explanation**: The last word is "moon" with length 4.

### Example 3
**Input**: `s = "luffy is still joyboy"`
**Output**: `6`
**Explanation**: The last word is "joyboy" with length 6.

---

## 2. Explanation
We need to find the last chunk of non-space characters.
The string might have trailing spaces (e.g., `"moon  "`).

### Approach 1: Helper Functions
Split the string by spaces, filter out empty strings, take the last one.
`s.split()` usually handles multiple spaces correctly in Python.

### Approach 2: Reverse Iteration (No Helpers - Interview Style)
1.  Start from the end of the string.
2.  Skip trailing spaces.
3.  Count characters until we hit a space or the beginning of the string.
-   **Time**: $O(n)$
-   **Space**: $O(1)$

---

## 3. Pseudo Code
```text
n = length(s)
length = 0
i = n - 1

# Skip trailing spaces
While i >= 0 AND s[i] == ' ':
    i--

# Count last word
While i >= 0 AND s[i] != ' ':
    length++
    i--

Return length
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        # Pythonic way (efficient and clean)
        # s.split() without arguments splits by whitespace and removes empty strings by default
        words = s.split()
        if not words:
            return 0
        return len(words[-1])

    def lengthOfLastWord_manual(self, s: str) -> int:
        # Interview style (manual iteration)
        i = len(s) - 1
        length = 0
        
        # 1. Skip trailing spaces
        while i >= 0 and s[i] == ' ':
            i -= 1
            
        # 2. Count characters of the last word
        while i >= 0 and s[i] != ' ':
            length += 1
            i -= 1
            
        return length
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(1)$ (Manual approach) or $O(n)$ (Split approach).

## 6. Example Walkthrough
`s = "   fly me   to   the moon  "`

1.  Start `i` at end.
2.  Skip trailing spaces: `i` moves back past the two spaces after "moon".
3.  Counts 'n', 'o', 'o', 'm'. `length` becomes 4.
4.  Next char is ' ', stop.

Result: 4.
