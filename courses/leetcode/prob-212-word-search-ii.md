---
layout: page
title: "212. Word Search II"
permalink: /courses/leetcode/prob-212-word-search-ii/
---

# 212. Word Search II

## 1. The Question
Given an `m x n` board of characters `board` and a list of strings `words`, return all words on the board.

Each word must be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once in a word.

### Example 1
**Input**:
```
board = [
  ["o","a","a","n"],
  ["e","t","a","e"],
  ["i","h","k","r"],
  ["i","f","l","v"]
]
words = ["oath","pea","eat","rain"]
```
**Output**: `["eat","oath"]`

---

## 2. Explanation
We need to search all `words` in the grid.
Naive DFS for each word is too slow if many words share prefixes.
Optimization: **Trie**.
1.  Insert all `words` into a Trie.
2.  Iterate every cell `(r, c)` in board.
3.  Start DFS from `(r, c)` using the Trie node structure.
    -   If we traverse to a Trie node `isEnd`, we found a word.
    -   Pruning: If current Trie node has no children (dead end), stop.
    -   Deduping: A found word shouldn't be added twice. Remove it from Trie or Use Set? Removing from Trie is optimization.

-   **Time**: $O(M \cdot N \cdot 4^L)$ where L is max word length. Trie optimization drastically reduces actual runtime by grouping prefixes.
-   **Space**: $O(\sum L)$ for Trie.

### Special Optimization
Remove found words from the Trie to prevent re-finding them and to prune branches early.

---

## 3. Pseudo Code
```text
root = TrieNode()
for w in words: root.insert(w)

res = []
def dfs(r, c, node):
    char = board[r][c]
    if char not in node.children: return
    
    nextNode = node.children[char]
    if nextNode.word: # Stored whole word at leaf in Insert
        res.append(nextNode.word)
        nextNode.word = None # Dedup
    
    board[r][c] = '#' # Visited
    
    for dr, dc in neighbors:
        dfs(r+dr, c+dc, nextNode)
        
    board[r][c] = char # Backtrack

for r in rows:
    for c in cols:
        dfs(r, c, root)
```

---

## 4. Optimal Code (Python)

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None  # Store the actual word at the end node

class Solution:
    def findWords(self, board: list[list[str]], words: list[str]) -> list[str]:
        # 1. Build Trie
        root = TrieNode()
        for w in words:
            node = root
            for char in w:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.word = w
        
        rows, cols = len(board), len(board[0])
        result = []
        
        def dfs(r, c, parent_node):
            char = board[r][c]
            
            # Check if this char exists in the current Trie branch
            if char not in parent_node.children:
                return
            
            curr_node = parent_node.children[char]
            
            # Found a word
            if curr_node.word:
                result.append(curr_node.word)
                curr_node.word = None  # Avoid duplicates
                
            # Mark visited
            board[r][c] = '#'
            
            # Explore neighbors
            if r > 0: dfs(r - 1, c, curr_node)
            if r < rows - 1: dfs(r + 1, c, curr_node)
            if c > 0: dfs(r, c - 1, curr_node)
            if c < cols - 1: dfs(r, c + 1, curr_node)
            
            # Backtrack
            board[r][c] = char
            
            # Optimization: Prune leaf nodes
            if not curr_node.children:
                del parent_node.children[char]

        # 2. Run DFS from each cell
        for r in range(rows):
            for c in range(cols):
                dfs(r, c, root)
                
        return result
```

---

## 5. Complexity
-   **Time**: $O(M \cdot N \cdot 4^L)$.
-   **Space**: $O(K \cdot L)$ for Trie.

## 6. Example Walkthrough
Words: `oath, pea`.
Trie: `o-a-t-h (word)`, `p-e-a (word)`.
Grid scan finds 'o'. Matches Trie 'o'.
DFS -> 'a' -> 't' -> 'h'. Found "oath".
Add to res. Remove "oath" mark.
Grid scan finds 'p'. Matches... found "pea".
