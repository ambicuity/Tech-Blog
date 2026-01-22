---
layout: page
title: "151. Reverse Words in a String"
permalink: /courses/leetcode/prob-151-reverse-words-in-a-string/
---

# 151. Reverse Words in a String

## 1. The Question
Given an input string `s`, reverse the order of the **words**.

A **word** is defined as a sequence of non-space characters. The **words** in `s` will be separated by at least one space.

Return a string of the words in reverse order concatenated by a single space.

Note that `s` may contain leading or trailing spaces or multiple spaces between two words. The returned string should only have a single space separating the words. Do not include any extra spaces.

### Example 1
**Input**: `s = "the sky is blue"`
**Output**: ` "blue is sky the"`

### Example 2
**Input**: `s = "  hello world  "`
**Output**: `"world hello"`
**Explanation**: Your reversed string should not contain leading or trailing spaces.

### Example 3
**Input**: `s = "a good   example"`
**Output**: `"example good a"`
**Explanation**: You need to reduce multiple spaces between two words to a single space in the reversed string.

---

## 2. Explanation
We need to:
1.  Remove leading/trailing spaces.
2.  Handle multiple internal spaces.
3.  Reverse the order of words.

### Approach 1: Built-in Split and Join (Pythonic)
Python's `split()` (with no args) automatically handles removing all whitespace (leading, trailing, and multiple spaces in between). Then we just reverse the list and join with a single space.

### Approach 2: Manual Two Pointers (In-place C++ Style)
If we couldn't use extra space (or were in C++):
1.  Reverse the entire string.
2.  Reverse each word individually.
3.  Clean up spaces.

Since strings are immutable in Python, Approach 1 is standard and most optimal.

---

## 3. Pseudo Code
```text
words = split(s) by whitespace
reverse words list
return join(words) with " "
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def reverseWords(self, s: str) -> str:
        # split() without arguments splits by ANY whitespace run 
        # and ignores empty strings
        words = s.split()
        
        # Reverse the list of words
        words.reverse()
        
        # Join with a single space
        return " ".join(words)
```

---

## 5. Complexity
-   **Time**: $O(n)$. Splitting, reversing, and joining all take linear time.
-   **Space**: $O(n)$ to store list of words.

## 6. Example Walkthrough
`s = "  a good   example  "`

1.  `s.split()`: Detects "a", "good", "example". Skips all extra spaces.
    `words = ["a", "good", "example"]`
2.  `words.reverse()`: `["example", "good", "a"]`
3.  `" ".join(...)`: `"example good a"`
