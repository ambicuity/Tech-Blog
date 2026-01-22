---
layout: page
title: "208. Implement Trie (Prefix Tree)"
permalink: /courses/leetcode/prob-208-implement-trie-prefix-tree/
---

# 208. Implement Trie (Prefix Tree)

## 1. The Question
A **Trie** (pronounced as "try") or **prefix tree** is a tree data structure used to efficiently store and retrieve keys in a dataset of strings. There are various applications of this data structure, such as autocomplete and spellchecker.

Implement the `Trie` class:
-   `Trie()` Initializes the trie object.
-   `void insert(String word)` Inserts the string `word` into the trie.
-   `boolean search(String word)` Returns `true` if the string `word` is in the trie (i.e., was inserted before), and `false` otherwise.
-   `boolean startsWith(String prefix)` Returns `true` if there is a previously inserted string `word` that has the prefix `prefix`, and `false` otherwise.

### Example 1
**Input**
`["Trie", "insert", "search", "search", "startsWith", "insert", "search"]`
`[[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]`
**Output**
`[null, null, true, false, true, null, true]`

---

## 2. Explanation
A Trie consists of nodes. Each node represents a character.
To support lowercase English letters, each node has an array of size 26 (or a HashMap).
Eache node also needs a flag `is_end_of_word` to mark if a word ends at this node.

Operations:
-   `insert`: Traverse down, creating nodes if missing. Mark last node as `is_end`.
-   `search`: Traverse down. If char missing, return False. If end of word matches `is_end`, return True.
-   `startsWith`: Traverse down. If keys missing, return False. If traversal completes, return True.

-   **Time**: $O(L)$ for each operation, where L is word length.
-   **Space**: $O(N \cdot L)$ total characters stored.

---

## 3. Pseudo Code
```text
class TrieNode:
    children = {}
    isEnd = False

class Trie:
    root = TrieNode()

    insert(word):
        curr = root
        for c in word:
            if c not in curr.children:
                curr.children[c] = TrieNode()
            curr = curr.children[c]
        curr.isEnd = True

    search(word):
        curr = root
        for c in word:
            if c not in curr.children: return False
            curr = curr.children[c]
        return curr.isEnd

    startsWith(prefix):
        curr = root
        for c in prefix:
            if c not in curr.children: return False
            curr = curr.children[c]
        return True
```

---

## 4. Optimal Code (Python)

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end = True

    def search(self, word: str) -> bool:
        current = self.root
        for char in word:
            if char not in current.children:
                return False
            current = current.children[char]
        return current.is_end

    def startsWith(self, prefix: str) -> bool:
        current = self.root
        for char in prefix:
            if char not in current.children:
                return False
            current = current.children[char]
        return True
```

---

## 5. Complexity
-   **Time**: $O(L)$ for insert, search, startsWith.
-   **Space**: $O(N \cdot L)$.

## 6. Example Walkthrough
1.  Insert "apple".
    -   `root -> a -> p -> p -> l -> e (isEnd=True)`.
2.  Search "app".
    -   `root -> a -> p -> p`. End node `p`. `isEnd` is False. Return False.
3.  StartsWith "app".
    -   `root -> a -> p -> p`. Exists. Return True.
