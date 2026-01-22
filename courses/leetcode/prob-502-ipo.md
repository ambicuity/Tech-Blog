---
layout: page
title: "502. IPO"
permalink: /courses/leetcode/prob-502-ipo/
---

# 502. IPO

## 1. The Question
Suppose LeetCode will start its **IPO** soon. In order to sell a good price of its shares to Venture Capital, LeetCode would like to work on some projects to increase its capital before the IPO. Since it has limited resources, it can only finish at most `k` distinct projects before the IPO. Help LeetCode design the best way to maximize its total capital after finishing at most `k` distinct projects.

You are given `n` projects where the `i`th project has a pure profit `profits[i]` and a minimum capital of `capital[i]` is needed to start it.

Initially, you have `w` capital. When you finish a project, you will obtain its pure profit and the profit will be added to your total capital.

Pick a list of **at most** `k` distinct projects from given projects to **maximize your final capital**, and return the final maximized capital.

### Example 1
**Input**: `k = 2, w = 0, profits = [1,2,3], capital = [0,1,1]`
**Output**: `4`
**Explanation**:
1.  Capital 0. Only project 0 (cap 0, prof 1) is available. Finish it. Capital -> 1.
2.  Capital 1. Projects 1 (cap 1) and 2 (cap 1) available. Pick Project 2 (prof 3). Capital -> 1+3=4.
Final 4.

---

## 2. Explanation
At any step, we can choose any project where `capital[i] <= current_capital`.
Among those available, we should ALWAYS pick the one with the **maximum profit**. This is a greedy approach.

Algorithm:
1.  Sort all projects by `capital` required (Min-Capital first).
2.  Use a **Max-Heap** to store the profits of **available** projects.
3.  In each of the `k` steps:
    -   Move all projects with `capital[i] <= w` from the sorted list to the Max-Heap.
    -   If heap empty, stop (cannot afford anything).
    -   Pop max profit from heap, add to `w`.

-   **Time**: $O(N \log N)$ for sorting + $O(k \log N)$ for heap ops.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
projects = sorted zip(capital, profits)
heap = []
i = 0

for _ in range(k):
    while i < n and projects[i].capital <= w:
        heappush(heap, -projects[i].profit)
        i += 1
        
    if not heap: break
    
    w += -heappop(heap)

return w
```

---

## 4. Optimal Code (Python)

```python
import heapq

class Solution:
    def findMaximizedCapital(self, k: int, w: int, profits: list[int], capital: list[int]) -> int:
        n = len(profits)
        # Pair capital with profits and sort by capital
        projects = []
        for i in range(n):
            projects.append((capital[i], profits[i]))
        projects.sort()
        
        max_heap = []
        i = 0
        
        for _ in range(k):
            # Push all projects that can be afforded currently into the heap
            while i < n and projects[i][0] <= w:
                # We push negative profit because Python has min-heap
                heapq.heappush(max_heap, -projects[i][1])
                i += 1
                
            # If no projects can be afforded, break
            if not max_heap:
                break
                
            # Select the most profitable project
            w += -heapq.heappop(max_heap)
            
        return w
```

---

## 5. Complexity
-   **Time**: $O(N \log N + K \log N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`k=2, w=0`. `P=[1,2,3], C=[0,1,1]`.
Projects: `(0,1), (1,2), (1,3)`. (Sorted).
1.  `w=0`. Available: `(0,1)`. Heap `[1]`. `i` moves to 1.
    -   Pop `1`. `w` becomes `1`.
2.  `w=1`. Available (`<=1`): `(1,2), (1,3)`. Heap `[3, 2]`. `i` moves to 3.
    -   Pop `3`. `w` becomes `1+3=4`.
Result 4.
