---
layout: page
title: "433. Minimum Genetic Mutation"
permalink: /courses/leetcode/prob-433-minimum-genetic-mutation/
---

# 433. Minimum Genetic Mutation

## 1. The Question
A gene string can be represented by an 8-character long string, with choices from `'A'`, `'C'`, `'G'`, and `'T'`.

Suppose we need to investigate a mutation from a gene string `startGene` to a gene string `endGene` where one mutation is defined as one single character changed in the gene string.

-   For example, `"AACCGGTT" --> "AACCGGTA"` is 1 mutation.

There is also a gene bank `bank` that records all the valid gene mutations. A gene must be in `bank` to make it a valid gene string.

Return the minimum number of mutations needed to mutate from `startGene` to `endGene`. If there is no such a mutation, return `-1`.

Note that the starting point is assumed to be valid, so it might not be included in the bank.

### Example 1
**Input**: `startGene = "AACCGGTT", endGene = "AACCGGTA", bank = ["AACCGGTA"]`
**Output**: `1`

### Example 2
**Input**: `startGene = "AACCGGTT", endGene = "AAACGGTA", bank = ["AACCGGTA","AAACGGTA","AACCGGTT","AAACGGTT"]`
**Output**: `2`

---

## 2. Explanation
This is classic BFS.
Start Node: `startGene`. Target: `endGene`. Valid Neighbors: Strings in `bank` that differ by exactly 1 char.
Since length is small (8) and alphabet is small (4), we can generate neighbors dynamically and check if in bank, OR iterate bank to find neighbors.
Given bank size is small (up to 10), checking bank is fast.

### Approach: BFS
1.  Add `startGene` to Queue. Depth 0.
2.  `seen` set.
3.  While Queue:
    -   Pop `curr`.
    -   Generate all possible mutations (change one char to A, C, G, T).
    -   If mutation same as `endGene` AND in `bank` (or if `curr` reaches `end` step).
    -   Actually `endGene` MUST be in `bank` to be valid target? Yes, "A gene must be in bank".
    -   Simpler: Loop through `bank`. If `bank_gene` differs by 1 from `curr`, it's a neighbor.

-   **Time**: $O(N \cdot L)$, where $N$ is bank size, $L$ is gene length (8).
-   **Space**: $O(N \cdot L)$.

---

## 3. Pseudo Code
```text
q = [(start, 0)]
visited = {start}
bank_set = Set(bank)

while q:
    gene, steps = q.pop(0)
    if gene == end: return steps
    
    for i in range(8):
        for char in "ACGT":
            mutated = gene[:i] + char + gene[i+1:]
            if mutated in bank_set and mutated not in visited:
                visited.add(mutated)
                q.append(mutated, steps+1)
return -1
```

---

## 4. Optimal Code (Python)

```python
from collections import deque

class Solution:
    def minMutation(self, startGene: str, endGene: str, bank: list[str]) -> int:
        bank_set = set(bank)
        
        # If endGene is not in bank, impossible
        if endGene not in bank_set:
            return -1
            
        queue = deque([(startGene, 0)])
        visited = {startGene}
        
        while queue:
            current, steps = queue.popleft()
            
            if current == endGene:
                return steps
                
            # Try changing each character
            for i in range(len(current)):
                original_char = current[i]
                for char in "ACGT":
                    if char == original_char:
                        continue
                        
                    # Create mutation
                    mutation = current[:i] + char + current[i+1:]
                    
                    if mutation in bank_set and mutation not in visited:
                        visited.add(mutation)
                        queue.append((mutation, steps + 1))
                        
        return -1
```

---

## 5. Complexity
-   **Time**: $O(B \cdot L^2)$ or $O(B \cdot L)$ depending on implementation. Here generating strings is $L^2$. Bank set check is $O(L)$. Total operations bounded by Bank Size B? No, bounded by $4^8$ in theory but constrained by bank.
-   **Space**: $O(B \cdot L)$.

## 6. Example Walkthrough
Start `AAAA`. End `AACC`. Bank `[AAAC, AACC]`.
1.  Q: `(AAAA, 0)`.
2.  Pop `AAAA`. Neighbors:
    -   `AAAC` (in bank). Push `(AAAC, 1)`.
3.  Pop `AAAC`. Neighbors:
    -   `AACC` (in bank). Push `(AACC, 2)`.
4.  Pop `AACC`. Found! Return 2.
