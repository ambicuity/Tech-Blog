---
layout: page
title: "290. Word Pattern"
permalink: /courses/leetcode/prob-290-word-pattern/
---

# 290. Word Pattern

## 1. The Question
Given a `pattern` and a string `s`, find if `s` follows the same pattern.

Here **follow** means a full match, such that there is a bijection between a letter in `pattern` and a **non-empty** word in `s`.

### Example 1
**Input**: `pattern = "abba", s = "dog cat cat dog"`
**Output**: `true`

### Example 2
**Input**: `pattern = "abba", s = "dog cat cat fish"`
**Output**: `false`

### Example 3
**Input**: `pattern = "aaaa", s = "dog cat cat dog"`
**Output**: `false`

---

## 2. Explanation
This is exactly the same as **205. Isomorphic Strings**, but instead of mapping `char -> char`, we map `char -> word`.

1.  Split `s` into `words`.
2.  If `len(pattern) != len(words)`, return False.
3.  Use two maps: `char_to_word` and `word_to_char`.
4.  Check for consistency.

-   **Time**: $O(N)$ where N is total characters in `s`.
-   **Space**: $O(U)$ where U is unique words.

---

## 3. Pseudo Code
```text
words = s.split()
if len(pattern) != len(words): Return False

map_char = {}
map_word = {}

For c, w in zip(pattern, words):
    If c in map_char and map_char[c] != w: Return False
    If w in map_word and map_word[w] != c: Return False
    
    map_char[c] = w
    map_word[w] = c

Return True
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def wordPattern(self, pattern: str, s: str) -> bool:
        words = s.split()
        if len(pattern) != len(words):
            return False
            
        char_to_word = {}
        word_to_char = {}
        
        for c, w in zip(pattern, words):
            if c in char_to_word:
                if char_to_word[c] != w:
                    return False
            elif w in word_to_char:
                if word_to_char[w] != c:
                    return False
            else:
                char_to_word[c] = w
                word_to_char[w] = c
                
        return True
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`pattern = "abba"`, `s = "dog cat cat dog"`

1.  `a, dog`: Map `a->dog`, `dog->a`.
2.  `b, cat`: Map `b->cat`, `cat->b`.
3.  `b, cat`: `b` in map? Yes. Maps to `cat`? Yes.
4.  `a, dog`: `a` in map? Yes. Maps to `dog`? Yes.
True.
