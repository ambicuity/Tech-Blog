---
layout: page
title: "3. Longest Substring Without Repeating Characters"
permalink: /courses/leetcode/prob-3-longest-substring-without-repeating-characters/
---

# 3. Longest Substring Without Repeating Characters

## 1. The Question
Given a string `s`, find the length of the **longest substring** without repeating characters.

### Example 1
**Input**: `s = "abcabcbb"`
**Output**: `3`
**Explanation**: The answer is "abc", with the length of 3.

### Example 2
**Input**: `s = "bbbbb"`
**Output**: `1`
**Explanation**: The answer is "b", with the length of 1.

### Example 3
**Input**: `s = "pwwkew"`
**Output**: `3`
**Explanation**: The answer is "wke", with the length of 3.
Notice that the answer must be a substring, "pwke" is a subsequence and not a substring.

---

## 2. Explanation
We want to maintain a window `[left, right]` such that it contains only unique characters. We want to maximize `right - left + 1`.

### Approach 1: Sliding Window using Set
1.  Use a set to store characters in the current window.
2.  Iterate `right` pointer.
3.  If `s[right]` is in set, we have a repetition. We must shrink the window from the left until `s[right]` is removed.
    -   Remove `s[left]` from set, `left++`. Repeat.
4.  Add `s[right]` to set.
5.  Update `max_len`.

### Approach 2: Optimized Map (Skip Left Pointer)
Instead of moving `left` one by one, we can jump.
Store the `last_index` of every character.
If we see `s[right]` and it was seen at `index`, we simply move `left` to `index + 1` (if that's ahead of current `left`).
-   **Time**: $O(n)$
-   **Space**: $O(min(m, n))$ where m is charset size.

---

## 3. Pseudo Code (Set Approach)
```text
char_set = Set()
left = 0
res = 0

For right from 0 to n-1:
    While s[right] in char_set:
        Remove s[left] from char_set
        left++
    
    Add s[right] to char_set
    res = max(res, right - left + 1)

Return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        char_set = set()
        left = 0
        max_length = 0
        
        for right in range(len(s)):
            # If current character is a duplicate, shrink window from left
            # until the character is removed
            while s[right] in char_set:
                char_set.remove(s[left])
                left += 1
                
            char_set.add(s[right])
            max_length = max(max_length, right - left + 1)
            
        return max_length

    # Optimized One (Map)
    def lengthOfLongestSubstring_opt(self, s: str) -> int:
        char_map = {} # char -> last_index
        left = 0
        max_length = 0
        
        for right, char in enumerate(s):
            # If char was seen and is inside the current window
            if char in char_map and char_map[char] >= left:
                # Move left to just after the previous occurrence
                left = char_map[char] + 1
            
            char_map[char] = right
            max_length = max(max_length, right - left + 1)
            
        return max_length
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(min(n, m))$ where m is size of alphabet (e.g. 128 for ASCII).

## 6. Example Walkthrough
`s = "abcabcbb"`

1.  `R=0 ('a')`. Set={'a'}. Max=1.
2.  `R=1 ('b')`. Set={'a','b'}. Max=2.
3.  `R=2 ('c')`. Set={'a','b','c'}. Max=3.
4.  `R=3 ('a')`. Duplicate!
    -   Remove 'a' (L=0). L=1.
    -   Add 'a' (R=3). Set={'b','c','a'}. Max=3.
5.  `R=4 ('b')`. Duplicate!
    -   Remove 'b' (L=1). L=2.
    -   Add 'b'. Set={'c','a','b'}. Max=3.
...
