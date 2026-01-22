---
layout: page
title: "210. Course Schedule II"
permalink: /courses/leetcode/prob-210-course-schedule-ii/
---

# 210. Course Schedule II

## 1. The Question
There are a total of `numCourses` courses you have to take, labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [ai, bi]` indicates that you must take course `bi` first if you want to take course `ai`.

Return the **ordering** of courses you should take to finish all courses. If there are many valid answers, return **any** of them. If it is impossible to finish all courses, return **an empty array**.

### Example 1
**Input**: `numCourses = 2, prerequisites = [[1,0]]`
**Output**: `[0,1]`
**Explanation**: Take 0, then 1.

### Example 2
**Input**: `numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]`
**Output**: `[0,2,1,3]` or `[0,1,2,3]`

---

## 2. Explanation
This is exactly the same as Course Schedule I, but instead of returning `True/False`, we return the **Topological Order**.
We collect the nodes as we pop them from the queue.

-   **Time**: $O(V + E)$.
-   **Space**: $O(V + E)$.

---

## 3. Pseudo Code
```text
adj = lists
indegree = [0]*n
for b, a in prereq:
    adj[a].append(b)
    indegree[b] += 1

q = [i for i in range(n) if indegree[i] == 0]
result = []

while q:
    u = q.pop(0)
    result.append(u)
    for v in adj[u]:
        indegree[v] -= 1
        if indegree[v] == 0:
            q.append(v)

if len(result) == n: return result
else: return []
```

---

## 4. Optimal Code (Python)

```python
from collections import deque

class Solution:
    def findOrder(self, numCourses: int, prerequisites: list[list[int]]) -> list[int]:
        adj = [[] for _ in range(numCourses)]
        indegree = [0] * numCourses
        
        for course, prereq in prerequisites:
            adj[prereq].append(course)
            indegree[course] += 1
            
        queue = deque([i for i in range(numCourses) if indegree[i] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in adj[node]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(result) == numCourses:
            return result
        else:
            return []
```

---

## 5. Complexity
-   **Time**: $O(V + E)$.
-   **Space**: $O(V + E)$.

## 6. Example Walkthrough
`4, [[1,0],[2,0],[3,1],[3,2]]`. (0->1, 0->2, 1->3, 2->3).
Indegrees: `0:0, 1:1, 2:1, 3:2`.
1.  Q: `[0]`.
2.  Pop `0`. Res: `[0]`. Decrement 1 and 2.
    -   Indegree 1 -> 0. Push 1.
    -   Indegree 2 -> 0. Push 2.
3.  Q: `[1, 2]`.
4.  Pop `1`. Res: `[0, 1]`. Decrement 3.
    -   Indegree 3 -> 1.
5.  Pop `2`. Res: `[0, 1, 2]`. Decrement 3.
    -   Indegree 3 -> 0. Push 3.
6.  Pop `3`. Res: `[0, 1, 2, 3]`.
Return `[0, 1, 2, 3]`.
