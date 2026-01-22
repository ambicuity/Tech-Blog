---
layout: page
title: "30. Substring with Concatenation of All Words"
permalink: /courses/leetcode/prob-30-substring-concatenation/
---

# 30. Substring with Concatenation of All Words

## 1. The Question
You are given a string `s` and an array of strings `words`. All the strings of `words` are of the **same length**.

A **concatenated substring** in `s` is a substring that contains all the strings of any permutation of `words` concatenated.
For example, if `words = ["ab","cd","ef"]`, then "abcdef", "abefcd", "cdabef", "cdefab", "efabcd", and "efcdab" are all concatenated strings. "acdbef" is not a concatenated substring because it is not the concatenation of any permutation of `words`.

Return the starting indices of all the concatenated substrings in `s`. You can return the answer in any order.

### Example 1
**Input**: `s = "barfoothefoobarman", words = ["foo","bar"]`
**Output**: `[0,9]`
**Explanation**:
At index 0: "barfoo". "bar" + "foo". (Concatenation of ["bar", "foo"])
At index 9: "foobar". "foo" + "bar". (Concatenation of ["foo", "bar"])

### Example 2
**Input**: `s = "wordgoodgoodgoodbestword", words = ["word","good","best","word"]`
**Output**: `[]`

### Example 3
**Input**: `s = "barfoofoobarthefoobarman", words = ["bar","foo","the"]`
**Output**: `[6,9,12]`

---

## 2. Explanation
This is a Hard Sliding Window problem.
Key constraint: **All words have the same length** `L`.
Total length of substring must be `total_len = len(words) * L`.

We need to check if a substring of length `total_len` consists exactly of the frequency map of `words`.

### Approach 1: Naive Sliding Window
Iterate every index `i`. Check substring `s[i : i+total_len]`.
Inside, split the substring into chunks of size `L`. Check if these chunks match the frequency map of `words`.
-   **Time**: $O(N \cdot M \cdot L)$ where M is number of words. Since checking takes $O(M \cdot L)$.

### Approach 2: Optimized Sliding Window (Offset-based)
We only need to start matching at offsets `0, 1, ..., L-1`.
Why? Because any valid substring starts at some index $k$. That index $k$ can be written as $i \cdot L + offset$.
If we fix an `offset` (e.g., 0), we essentially have an array of "tokens" of size `L`.
`s = "bar foo the foo bar ..."` -> `["bar", "foo", "the", "foo", "bar", ...]`.
Now this becomes: **Find all subarrays in this token-array that match the counts in `words`**.
This is exactly the "Minimum Window Substring" or "Anagram" problem, but on *tokens* instead of *chars*.

1.  Calculcate `word_count` map.
2.  Loop `i` from `0` to `L-1`.
3.  Inside, run a sliding window over tokens: `left` and `right`.
    -   Move `right` by step `L`. Add word to `current_count`.
    -   If word count exceeds expected, shrink from `left` until valid.
    -   If `right - left` corresponds to total words, we found a match at `left`.

-   **Time**: $O(N \cdot L)$ or just $O(N)$ since the inner loop steps by L, and outer loop runs L times.
-   **Space**: $O(M)$ for the maps.

---

## 3. Pseudo Code
```text
L = len(words[0])
count = Counter(words)
res = []

For i from 0 to L-1:
    left = i
    right = i
    cur_count = {}
    
    While right + L <= len(s):
        w = s[right : right+L]
        right += L
        
        if w in count:
            cur_count[w]++
            
            # If we have too many of word w, shrink from left
            While cur_count[w] > count[w]:
                left_w = s[left : left+L]
                left += L
                cur_count[left_w]--
            
            # Check length
            if right - left == total_len:
                res.append(left)
                
        else:
            # Word not in list at all - reset window completely
            cur_count.clear()
            left = right
            
Return res
```

---

## 4. Optimal Code (Python)

```python
from collections import Counter

class Solution:
    def findSubstring(self, s: str, words: list[str]) -> list[int]:
        if not s or not words:
            return []
            
        word_len = len(words[0])
        word_count = len(words)
        total_len = word_len * word_count
        
        # Frequency map of required words
        required = Counter(words)
        
        result = []
        
        # We only need to start from 0 to word_len-1
        # because the window moves in steps of word_len
        for i in range(word_len):
            left = i
            right = i
            window_counts = Counter()
            
            # Sliding window with step size word_len
            while right + word_len <= len(s):
                # Acquire word at right end
                w = s[right : right + word_len]
                right += word_len
                
                if w in required:
                    window_counts[w] += 1
                    
                    # While we have excess of this word, shrink from left
                    while window_counts[w] > required[w]:
                        left_w = s[left : left + word_len]
                        left += word_len
                        window_counts[left_w] -= 1
                    
                    # If window size matches total length, it's a valid match
                    # (We know counts are <= required due to while loop,
                    # so if lengths match, counts must match exactly)
                    if right - left == total_len:
                        result.append(left)
                        
                else:
                    # Invalid word found; resets the sequence
                    window_counts.clear()
                    left = right
                    
        return result
```

---

## 5. Complexity
-   **Time**: $O(N)$. We visit each character roughly twice (once for each of the `L` offsets, but stride is `L`).
-   **Space**: $O(M)$ where M is number of unique words + map overhead.

## 6. Example Walkthrough
`s = "barfoothefoobarman"`, `words = ["foo", "bar"]`
`L=3`, `total=6`.

1.  `i=0`:
    -   `R=0`: Read "bar". Valid. `win={'bar':1}`. Size=3.
    -   `R=3`: Read "foo". Valid. `win={'bar':1, 'foo':1}`. Size=6.
    -   `Size == 6`. **Match at 0**.
    -   `R=6`: Read "the". INVALID. Reset. `win={}`. `L=9, R=9`.
    -   `R=9`: Read "foo". `win={'foo':1}`.
    -   `R=12`: Read "bar". `win={'foo':1, 'bar':1}`. Size=6.
    -   `Size == 6`. **Match at 9**.
    -   `R=15`: Read "man". INVALID.

2.  `i=1`: "arf", "oot", "hef"... (No matches)
3.  `i=2`: "rfo", "oth", "efo"... (No matches)

Result: `[0, 9]`.
