---
layout: page
title: "127. Word Ladder"
permalink: /courses/leetcode/prob-127-word-ladder/
---

# 127. Word Ladder

## 1. The Question
A **transformation sequence** from word `beginWord` to word `endWord` using a dictionary `wordList` is a sequence of words `beginWord -> s1 -> s2 -> ... -> sk` such that:
1.  Every adjacent pair of words differs by a single letter.
2.  Every `si` for `1 <= i <= k` is in `wordList`. Note that `beginWord` does not need to be in `wordList`.
3.  `sk == endWord`.

Given two words, `beginWord` and `endWord`, and a dictionary `wordList`, return the **number of words** in the **shortest transformation sequence** from `beginWord` to `endWord`, or `0` if no such sequence exists.

### Example 1
**Input**: `beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]`
**Output**: `5`
**Explanation**: `"hit" -> "hot" -> "dot" -> "dog" -> "cog"`, length 5.

---

## 2. Explanation
This is effectively the same problem as "Minimum Genetic Mutation", but with lowercase English letters (26 possible chars) and potentially longer words or larger lists.
Standard BFS.

Optimization:
Instead of iterating through `wordList` to find neighbors (which takes $O(N \cdot L)$), we generate all possible transformations ($O(26 \cdot L)$) and check if they exist in `wordList` (set check $O(L)$).
Total processing per word: $O(26 \cdot L^2)$.
If $N$ is large and $L$ is small, this is better.

-   **Time**: $O(M^2 \cdot N)$ where M is word length.
-   **Space**: $O(M \cdot N)$.

---

## 3. Pseudo Code
```text
words = Set(wordList)
if endWord not in words: return 0

q = [(begin, 1)]
visited = {begin}

while q:
    w, dist = q.pop(0)
    if w == end: return dist
    
    for i in 0..len(w):
        original = w[i]
        for c in 'a'..'z':
            if c == original: continue
            new_w = w[:i] + c + w[i+1:]
            
            if new_w in words and new_w not in visited:
                visited.add(new_w)
                q.append(new_w, dist+1)

return 0
```

---

## 4. Optimal Code (Python)

```python
from collections import deque
import string

class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: list[str]) -> int:
        word_set = set(wordList)
        if endWord not in word_set:
            return 0
            
        queue = deque([(beginWord, 1)])
        visited = {beginWord}
        
        while queue:
            word, length = queue.popleft()
            
            if word == endWord:
                return length
            
            # Try changing each char
            for i in range(len(word)):
                original_char = word[i]
                
                # Check all 26 lowercase letters
                for char in string.ascii_lowercase:
                    if char == original_char:
                        continue
                        
                    new_word = word[:i] + char + word[i+1:]
                    
                    if new_word in word_set and new_word not in visited:
                        visited.add(new_word)
                        queue.append((new_word, length + 1))
                        
        return 0
```

---

## 5. Complexity
-   **Time**: $O(N \cdot M^2)$ where N is number of words, M is length.
-   **Space**: $O(N \cdot M)$.

## 6. Example Walkthrough
`hit -> cog`
1.  `hit`. Neighbors: `hot` (in list). Push `hot(2)`.
2.  `hot`. Neighbors: `dot, lot`. Push `dot(3), lot(3)`.
3.  `dot`. Neighbors: `dog`. Push `dog(4)`.
4.  `lot`. Neighbors: `log`. Push `log(4)`.
5.  `dog`. Neighbors: `cog`. Push `cog(5)`.
6.  `cog` Found. Return 5.
