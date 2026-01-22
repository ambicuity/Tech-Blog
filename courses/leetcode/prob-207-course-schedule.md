---
layout: page
title: "207. Course Schedule"
permalink: /courses/leetcode/prob-207-course-schedule/
---

# 207. Course Schedule

## 1. The Question
There are a total of `numCourses` courses you have to take, labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [ai, bi]` indicates that you must take course `bi` first if you want to take course `ai`.
-   For example, the pair `[0, 1]` indicates that to take course `0` you have to first take course `1`.

Return `true` if you can finish all courses. Otherwise, return `false`.

### Example 1
**Input**: `numCourses = 2, prerequisites = [[1,0]]`
**Output**: `true`
**Explanation**: Take 0, then 1.

### Example 2
**Input**: `numCourses = 2, prerequisites = [[1,0],[0,1]]`
**Output**: `false`
**Explanation**: Cycle detected.

---

## 2. Explanation
This is a **Cycle Detection** problem in a Directed Graph.
Graph: Courses are nodes. Prerequisite `b -> a` is edge `b -> a`.
If there is a cycle, we can't finish.
Also allows checking via **Topological Sort** (Kahn's Algorithm). If we can consume all nodes, True.

### Approach: Kahn's Algorithm (BFS)
1.  Count in-degree of all nodes.
2.  Add nodes with in-degree 0 to Queue.
3.  While Queue not empty:
    -   Pop `node`. Increment `count`.
    -   For each neighbor:
        -   Decrement in-degree.
        -   If in-degree hits 0, push to Queue.
4.  If `count == numCourses`, True. Else False (cycle).

-   **Time**: $O(V + E)$.
-   **Space**: $O(V + E)$.

---

## 3. Pseudo Code
```text
adj = lists
indegree = [0]*n
for b, a in prereq:
    adj[a].append(b) # a is prereq for b
    indegree[b] += 1

q = [i for i in range(n) if indegree[i] == 0]
count = 0

while q:
    u = q.pop(0)
    count += 1
    for v in adj[u]:
        indegree[v] -= 1
        if indegree[v] == 0:
            q.append(v)

return count == n
```

---

## 4. Optimal Code (Python)

```python
from collections import deque

class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        # Build graph and in-degrees
        # Edge: prereq -> course (bi -> ai)
        adj = [[] for _ in range(numCourses)]
        indegree = [0] * numCourses
        
        for course, prereq in prerequisites:
            adj[prereq].append(course)
            indegree[course] += 1
            
        # Queue of courses with no prerequisites
        queue = deque([i for i in range(numCourses) if indegree[i] == 0])
        count = 0
        
        while queue:
            node = queue.popleft()
            count += 1
            
            for neighbor in adj[node]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
                    
        return count == numCourses
```

---

## 5. Complexity
-   **Time**: $O(V + E)$.
-   **Space**: $O(V + E)$.

## 6. Example Walkthrough
2 courses, `[1,0]` (0->1).
Graph: `0 -> 1`.
Indegrees: `0:0, 1:1`.
1.  Q: `[0]`.
2.  Pop `0`. Count=1. Neighbors `[1]`.
    -   Indegree[1] becomes 0. Push `1`.
3.  Q: `[1]`.
4.  Pop `1`. Count=2.
5.  Count(2) == Num(2). True.
