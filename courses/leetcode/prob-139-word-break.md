---
layout: page
title: "139. Word Break"
permalink: /courses/leetcode/prob-139-word-break/
---

# 139. Word Break

## 1. The Question
Given a string `s` and a dictionary of strings `wordDict`, return `true` if `s` can be segmented into a space-separated sequence of one or more dictionary words.

Note that the same word in the dictionary may be reused multiple times in the segmentation.

### Example 1
**Input**: `s = "leetcode", wordDict = ["leet","code"]`
**Output**: `true`

### Example 2
**Input**: `s = "applepenapple", wordDict = ["apple","pen"]`
**Output**: `true`

---

## 2. Explanation
DP State: `dp[i]` is True if substring `s[0...i]` can be segmented.
To calculate `dp[i]`:
Check all possible split points `j < i`.
If `dp[j]` is True (prefix `s[0...j]` valid) AND `s[j...i]` is in `wordDict`, then `dp[i]` is True.

Base case: `dp[0] = True` (empty string).

-   **Time**: $O(N^2 \cdot K)$. String slice/hashing takes time. Max word length optimization ($O(N \cdot M)$).
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
dp = [False] * (n + 1)
dp[0] = True

for i in range(1, n + 1):
    for w in wordDict:
        if i >= len(w) and s[i-len(w):i] == w:
             if dp[i-len(w)]:
                 dp[i] = True
                 break
return dp[n]
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def wordBreak(self, s: string, wordDict: list[str]) -> bool:
        dp = [False] * (len(s) + 1)
        dp[0] = True # Empty string is valid
        
        # Optimization: Only check substrings of length relevant to wordDict
        word_set = set(wordDict)
        max_len = max(len(w) for w in wordDict) if wordDict else 0
        
        for i in range(1, len(s) + 1):
            # Check substrings ending at i
            # Look back at most max_len chars
            for j in range(max(0, i - max_len), i):
                if dp[j] and s[j:i] in word_set:
                    dp[i] = True
                    break
        
        return dp[len(s)]
```

---

## 5. Complexity
-   **Time**: $O(N \cdot M)$, where M is max word length.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`"leetcode"`, `["leet", "code"]`.
1.  `dp[0]=True`.
2.  `i=1..4`. No match.
3.  `i=4`. `j=0`. `dp[0]` True. `s[0:4] = "leet"`. Match. `dp[4]=True`.
4.  `i=5..7`. No match.
5.  `i=8`. `j=4`. `dp[4]` True. `s[4:8] = "code"`. Match. `dp[8]=True`.
Result True.
