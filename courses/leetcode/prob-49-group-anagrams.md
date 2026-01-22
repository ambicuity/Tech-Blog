---
layout: page
title: "49. Group Anagrams"
permalink: /courses/leetcode/prob-49-group-anagrams/
---

# 49. Group Anagrams

## 1. The Question
Given an array of strings `strs`, group the **anagrams** together. You can return the answer in any order.

An **Anagram** is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.

### Example 1
**Input**: `strs = ["eat","tea","tan","ate","nat","bat"]`
**Output**: `[["bat"],["nat","tan"],["ate","eat","tea"]]`

### Example 2
**Input**: `strs = [""]`
**Output**: `[[""]]`

### Example 3
**Input**: `strs = ["a"]`
**Output**: `[["a"]]`

---

## 2. Explanation
We need to group words that have the same "signature".
The signature of an anagram is its sorted letters or its character counts.

### Approach 1: Sort as Key
For each string `s`, sort it to get the key.
`"eat" -> "aet"`. `"tea" -> "aet"`.
Use a hash map to group: `Map<String, List<String>>`.
-   **Time**: $O(N \cdot K \log K)$ where N is number of strings, K is max length of string.
-   **Space**: $O(N \cdot K)$.

### Approach 2: Count as Key (Optimal)
Instead of sorting, use a tuple of character counts (26 integers) as the key.
`"eat" -> (1, 0, 0, ..., 1, 0, ..., 1)` (counts of a, b, c... e... t)
-   **Time**: $O(N \cdot K)$. We don't sort.
-   **Space**: $O(N \cdot K)$.

---

## 3. Pseudo Code
```text
map = default_dict(list)

For s in strs:
    count = [0] * 26
    For c in s:
        count[ord(c) - ord('a')]++
    
    key = tuple(count)
    map[key].append(s)

Return map.values()
```

---

## 4. Optimal Code (Python)

```python
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        anagrams = defaultdict(list)
        
        for s in strs:
            # Create a character count key (a-z)
            count = [0] * 26
            for c in s:
                count[ord(c) - ord('a')] += 1
            
            # Use tuple as key since list is not hashable
            anagrams[tuple(count)].append(s)
            
        return list(anagrams.values())
```

---

## 5. Complexity
-   **Time**: $O(N \cdot K)$.
-   **Space**: $O(N \cdot K)$.

## 6. Example Walkthrough
`strs = ["eat", "tea", "tan"]`

1.  `"eat"`. Key: `(1,0,0,0,1,...,1,...)`. Map[`key`] = `["eat"]`.
2.  `"tea"`. Key: Same. Map[`key`] = `["eat", "tea"]`.
3.  `"tan"`. Key: different. Map[`key2`] = `["tan"]`.

Result: `[["eat", "tea"], ["tan"]]`.
