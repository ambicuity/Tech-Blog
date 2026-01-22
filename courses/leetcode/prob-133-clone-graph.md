---
layout: page
title: "133. Clone Graph"
permalink: /courses/leetcode/prob-133-clone-graph/
---

# 133. Clone Graph

## 1. The Question
Given a reference of a node in a **connected** undirected graph.

Return a **deep copy** (clone) of the graph.

Each node in the graph contains a value (`int`) and a list (`List[Node]`) of its neighbors.

### Example 1
**Input**: adjList = [[2,4],[1,3],[2,4],[1,3]]
**Output**: [[2,4],[1,3],[2,4],[1,3]]

---

## 2. Explanation
We need to traverse the graph and clone each node.
Since there might be cycles, we must keep track of visited nodes to avoid infinite loops and to link back to already created clones.

### Approach: DFS/BFS with Hash Map
Map `original_node -> clone_node`.
1.  Start at `node`.
2.  Check if `node` is in map.
    -   If yes, return `map[node]`.
    -   If no, create `clone`, add to map.
    -   Iterate neighbors. For each neighbor, recursively call clone logic and append to `clone.neighbors`.

-   **Time**: $O(N + E)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
map = {}

def dfs(node):
    if not node: return None
    if node in map: return map[node]
    
    clone = Node(node.val)
    map[node] = clone
    
    for neighbor in node.neighbors:
        clone.neighbors.append(dfs(neighbor))
        
    return clone
```

---

## 4. Optimal Code (Python)

```python
"""
# Definition for a Node.
class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []
"""

class Solution:
    def cloneGraph(self, node: 'Node') -> 'Node':
        if not node:
            return None
            
        visited = {}
        
        def dfs(original_node):
            if original_node in visited:
                return visited[original_node]
                
            # Create clone
            clone_node = Node(original_node.val)
            visited[original_node] = clone_node
            
            # Clone neighbors
            for neighbor in original_node.neighbors:
                clone_node.neighbors.append(dfs(neighbor))
                
            return clone_node
            
        return dfs(node)
```

---

## 5. Complexity
-   **Time**: $O(V + E)$.
-   **Space**: $O(V)$.

## 6. Example Walkthrough
1.  `DFS(1)`. Create `Clone(1)`. Map: `{1: C1}`.
    -   Neighbors of 1: `[2, 4]`.
    -   `DFS(2)`. Create `C2`. Map: `{1:C1, 2:C2}`.
        -   Neighbors of 2: `[1, 3]`.
        -   `DFS(1)` -> Returns `C1`.
        -   `DFS(3)`. Create `C3`. Map: `{..., 3:C3}`.
            -   Neighbors of 3: `[2, 4]`.
            -   `DFS(2)` -> Returns `C2`.
            -   `DFS(4)` -> ...
    -   `C1.neighbors` gets `C2` and `C4`.
Result: Deep copy.
