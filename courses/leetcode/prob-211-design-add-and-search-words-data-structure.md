---
layout: page
title: "211. Design Add and Search Words Data Structure"
permalink: /courses/leetcode/prob-211-design-add-and-search-words-data-structure/
---

# 211. Design Add and Search Words Data Structure

## 1. The Question
Design a data structure that supports adding new words and finding if a string matches any previously added string.

Implement the `WordDictionary` class:
-   `WordDictionary()` Initializes the object.
-   `void addWord(word)` Adds `word` to the data structure, it can be matched later.
-   `bool search(word)` Returns `true` if there is any string in the data structure that matches `word` or `false` otherwise. `word` may contain dots `'.'` where dots can be matched with any letter.

### Example 1
**Input**
`["WordDictionary","addWord","addWord","addWord","search","search","search","search"]`
`[[],["bad"],["dad"],["mad"],["pad"],["bad"],[".ad"],["b.."]]`
**Output**
`[null,null,null,null,false,true,true,true]`

---

## 2. Explanation
Standard Trie, but `search` needs to handle `.`.
If char is `.`, we must recursively search **all** children of the current node. If any returns True, then True.

-   **Time**:
    -   `addWord`: $O(L)$.
    -   `search`: Worst case $O(26^L)$ if all are dots (searching all paths).
-   **Space**: $O(N \cdot L)$.

---

## 3. Pseudo Code
```text
addWord: standard Insert.

search(word):
    return dfs(root, 0)

dfs(node, i):
    if i == len(word): return node.isEnd
    
    char = word[i]
    if char == '.':
        for child in node.children.values():
            if dfs(child, i+1): return True
        return False
    else:
        if char not in node.children: return False
        return dfs(node.children[char], i+1)
```

---

## 4. Optimal Code (Python)

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class WordDictionary:

    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word: str) -> None:
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end = True

    def search(self, word: str) -> bool:
        return self._search_node(self.root, word, 0)
        
    def _search_node(self, node, word, index):
        # Base case: if we have reached the end of the word
        if index == len(word):
            return node.is_end
        
        char = word[index]
        
        if char == '.':
            # Try all children
            for child in node.children.values():
                if self._search_node(child, word, index + 1):
                    return True
            return False
        else:
            # Regular character match
            if char not in node.children:
                return False
            return self._search_node(node.children[char], word, index + 1)
```

---

## 5. Complexity
-   **Time**: $O(L)$ normal search, $O(26^L)$ for wildcard.
-   **Space**: $O(N \cdot L)$.

## 6. Example Walkthrough
Words: `bad`, `dad`, `mad`.
Search `.ad`.
1.  `Root`. Index 0. Char `.`.
2.  Iterate children: `b`, `d`, `m`.
    -   Try `b`. Next char `a`. Match. Next `d`. Match. Return True.
    -   (If `b` failed, try `d`...).
Result: True.
