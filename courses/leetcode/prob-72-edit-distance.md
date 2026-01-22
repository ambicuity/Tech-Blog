---
layout: page
title: "72. Edit Distance"
permalink: /courses/leetcode/prob-72-edit-distance/
---

# 72. Edit Distance

## 1. The Question
Given two strings `word1` and `word2`, return the minimum number of operations required to convert `word1` to `word2`.

You have the following three operations permitted on a word:
1.  Insert a character
2.  Delete a character
3.  Replace a character

### Example 1
**Input**: `word1 = "horse", word2 = "ros"`
**Output**: `3`
**Explanation**:
horse -> rorse (replace 'h' with 'r')
rorse -> rose (remove 'r')
rose -> ros (remove 'e')

---

## 2. Explanation
Standard DP.
`dp[i][j]` = min ops to convert `word1[0..i]` to `word2[0..j]`.
Transitions:
If `word1[i-1] == word2[j-1]`: `dp[i][j] = dp[i-1][j-1]` (No op needed).
Else:
`1 + min(`
  `dp[i-1][j]`,    (Delete from word1)
  `dp[i][j-1]`,    (Insert into word1 / Delete from word2)
  `dp[i-1][j-1]`   (Replace)
`)`

-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(M \cdot N)$.

---

## 3. Pseudo Code
```text
for i in 0..m: dp[i][0] = i
for j in 0..n: dp[0][j] = j

for i in 1..m:
    for j in 1..n:
        if w1[i-1] == w2[j-1]: dp[i][j] = dp[i-1][j-1]
        else: dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Base cases
        for i in range(m + 1):
            dp[i][0] = i # Deleting all chars
        for j in range(n + 1):
            dp[0][j] = j # Inserting all chars
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i-1] == word2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],    # Delete
                        dp[i][j-1],    # Insert
                        dp[i-1][j-1]   # Replace
                    )
                    
        return dp[m][n]
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N)$.
-   **Space**: $O(M \cdot N)$.

## 6. Example Walkthrough
`horse`, `ros`.
... after filling ... returns 3.
