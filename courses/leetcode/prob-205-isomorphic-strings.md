---
layout: page
title: "205. Isomorphic Strings"
permalink: /courses/leetcode/prob-205-isomorphic-strings/
---

# 205. Isomorphic Strings

## 1. The Question
Given two strings `s` and `t`, determine if they are isomorphic.
Two strings `s` and `t` are isomorphic if the characters in `s` can be replaced to get `t`.
All occurrences of a character must be replaced with another character while preserving the order of characters. No two characters may map to the same character, but a character may map to itself.

### Example 1
**Input**: `s = "egg", t = "add"`
**Output**: `true`

### Example 2
**Input**: `s = "foo", t = "bar"`
**Output**: `false`

### Example 3
**Input**: `s = "paper", t = "title"`
**Output**: `true`

---

## 2. Explanation
We need a 1-to-1 mapping (Bijection) between characters of `s` and `t`.
-   `e` -> `a`
-   `g` -> `d`
If `s[i]` maps to `t[i]`, it must ALWAYS map to `t[i]`.
AND `t[i]` must NOT be mapped to by any other character.

### Approach: Two Hash Maps
1.  `map_s_to_t`: mapping from source char to target char.
2.  `map_t_to_s`: mapping from target char to source char (to prevent many-to-one).

Iterate `i` from `0` to `n`.
-   Char `c1 = s[i]`, `c2 = t[i]`.
-   If `c1` in map, check if `map[c1] == c2`. If not, false.
-   If `c2` in reverse map, check if `reverse_map[c2] == c1`. If not, false.
-   Add to maps.

-   **Time**: $O(n)$
-   **Space**: $O(1)$ (Ascii size).

---

## 3. Pseudo Code
```text
s_map = {}
t_map = {}

For i from 0 to n-1:
    c1 = s[i]
    c2 = t[i]
    
    If (c1 in s_map and s_map[c1] != c2) OR (c2 in t_map and t_map[c2] != c1):
        Return False
        
    s_map[c1] = c2
    t_map[c2] = c1

Return True
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def isIsomorphic(self, s: str, t: str) -> bool:
        map_s_t = {}
        map_t_s = {}
        
        for c1, c2 in zip(s, t):
            # Case 1: s char already mapped, check consistency
            if c1 in map_s_t:
                if map_s_t[c1] != c2:
                    return False
            
            # Case 2: t char already mapped, check consistency
            elif c2 in map_t_s:
                if map_t_s[c2] != c1:
                    return False
            
            # Case 3: New mapping
            else:
                map_s_t[c1] = c2
                map_t_s[c2] = c1
                
        return True
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`s="foo", t="bar"`

1.  `f, b`. Map `f->b`, `b->f`.
2.  `o, a`. Map `o->a`, `a->o`.
3.  `o, r`.
    -   `o` is in map. `map[o] ('a') != 'r'`. Return False.
