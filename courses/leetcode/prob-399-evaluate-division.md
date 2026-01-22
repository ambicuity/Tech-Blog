---
layout: page
title: "399. Evaluate Division"
permalink: /courses/leetcode/prob-399-evaluate-division/
---

# 399. Evaluate Division

## 1. The Question
You are given an array of variable pairs `equations` and an array of real numbers `values`, where `equations[i] = [Ai, Bi]` and `values[i]` represent the equation `Ai / Bi = values[i]`. Each `Ai` or `Bi` is a string that represents a single variable.

You are also given some `queries`, where `queries[j] = [Cj, Dj]` represents the `jth` query where you must find the answer for `Cj / Dj = ?`.

Return the answers to all queries. If a single answer cannot be determined, return `-1.0`.

**Note**: The input is always valid. You may assume that evaluating the queries will not result in division by zero and that there is no contradiction.

### Example 1
**Input**:
`equations = [["a","b"],["b","c"]]`, `values = [2.0,3.0]`
`queries = [["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]]`
**Output**: `[6.00000,0.50000,-1.00000,1.00000,-1.00000]`
**Explanation**:
Given: `a / b = 2.0`, `b / c = 3.0`
`a / c = (a / b) * (b / c) = 2.0 * 3.0 = 6.0`
`b / a = 1 / (a / b) = 1 / 2.0 = 0.5`
`a / e` undefined (e unknown).
`a / a = 1.0`
`x / x` undefined (x unknown).

---

## 2. Explanation
This is a graph problem.
Variables are nodes. Equations are directed edges with weights.
`a / b = 2.0` means edge `a -> b` with weight `2.0`.
Implies `b -> a` with weight `1 / 2.0 = 0.5`.

Query `a / c` is finding a path from `a` to `c`. The result is the **product** of weights along the path.
`a -> b (2.0) -> c (3.0)`. Result `2.0 * 3.0 = 6.0`.

### Approach: Graph + BFS/DFS
1.  Build Graph: `Adj[A] = (B, val)`. `Adj[B] = (A, 1/val)`.
2.  For each query `(start, end)`:
    -   If `start` or `end` not in graph, return -1.
    -   Run BFS/DFS from `start` to find `end`.
    -   Maintain running product.

-   **Time**: $O(Q \cdot (V + E))$. For each query, we traverse graph.
-   **Space**: $O(V + E)$.

---

## 3. Pseudo Code
```text
graph = collections.defaultdict(dict)
for (a, b), val in equations:
    graph[a][b] = val
    graph[b][a] = 1 / val

def bfs(start, end):
    if start not in graph or end not in graph: return -1.0
    queue = [(start, 1.0)]
    visited = {start}
    
    while queue:
        curr, prod = queue.pop(0)
        if curr == end: return prod
        
        for neighbor, weight in graph[curr].items():
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, prod * weight))
                
    return -1.0
```

---

## 4. Optimal Code (Python)

```python
from collections import defaultdict, deque

class Solution:
    def calcEquation(self, equations: list[list[str]], values: list[float], queries: list[list[str]]) -> list[float]:
        # 1. Build Graph
        # graph[a][b] = weight means a / b = weight
        graph = defaultdict(dict)
        for (a, b), val in zip(equations, values):
            graph[a][b] = val
            graph[b][a] = 1.0 / val
            
        def bfs(start, end):
            if start not in graph or end not in graph:
                return -1.0
            
            queue = deque([(start, 1.0)]) # (current_node, current_product)
            visited = {start}
            
            while queue:
                curr, product = queue.popleft()
                
                if curr == end:
                    return product
                
                for neighbor, weight in graph[curr].items():
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, product * weight))
                        
            return -1.0

        return [bfs(q[0], q[1]) for q in queries]
```

---

## 5. Complexity
-   **Time**: $O(N \cdot (V + E))$. N queries.
-   **Space**: $O(V + E)$.

## 6. Example Walkthrough
`a/b=2, b/c=3`. Graph: `a->b(2), b->c(3), b->a(0.5), c->b(0.33)`.
Query `a/c`:
1.  BFS start `a`. Q: `[(a, 1)]`. Visited: `{a}`.
2.  Pop `a`. Neighbors: `b(2)`.
    -   Push `(b, 1*2=2)`. Visited: `{a, b}`.
3.  Pop `b`. Neighbors: `a(0.5)`, `c(3)`.
    -   `a` visited.
    -   `c` unvisited. Push `(c, 2*3=6)`. Visited: `{a, b, c}`.
4.  Pop `c`. `c == end`. Return 6.
