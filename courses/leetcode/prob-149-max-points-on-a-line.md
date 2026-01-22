---
layout: page
title: "149. Max Points on a Line"
permalink: /courses/leetcode/prob-149-max-points-on-a-line/
---

# 149. Max Points on a Line

## 1. The Question
Given an array of `points` where `points[i] = [xi, yi]`, return the maximum number of points that lie on the same straight line.

### Example 1
**Input**: `points = [[1,1],[2,2],[3,3]]`
**Output**: `3`

---

## 2. Explanation
For each point $P_i$, calculate slope to all other points $P_j$.
Points with same slope from $P_i$ are collinear.
Slope $m = (y_j - y_i) / (x_j - x_i)$.
Special case: $x_j - x_i = 0$ (Vertical line).
Store slopes in a HashMap.

Outer loop $O(N)$. Inner loop $O(N)$.
Compute GCD for slope to avoid floating point issues (`dy/dx`, simplify by GCD).
Slope Key: `(dy / g, dx / g)`.

-   **Time**: $O(N^2 \log (\text{coordinate}))$. GCD takes log.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
max_pts = 1
for i in 0..n:
    slopes = {}
    for j in i+1..n:
        dy, dx = pts[j].y - pts[i].y, pts[j].x - pts[i].x
        g = gcd(dy, dx)
        slope = (dy//g, dx//g)
        slopes[slope] += 1
    max_pts = max(max_pts, max(slopes.values()) + 1)
return max_pts
```

---

## 4. Optimal Code (Python)

```python
from collections import defaultdict
import math

class Solution:
    def maxPoints(self, points: list[list[int]]) -> int:
        n = len(points)
        if n < 3:
            return n
            
        max_points = 1
        
        for i in range(n):
            slopes = defaultdict(int)
            for j in range(i + 1, n):
                p1 = points[i]
                p2 = points[j]
                
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                
                # Normalize slope using GCD
                common = math.gcd(dx, dy)
                
                # Tuple as key for dictionary
                slope = (dx // common, dy // common)
                
                slopes[slope] += 1
                
            # If slopes is empty (all duplicates of i, or i is last), iterate won't run much.
            # But the max from 'i' perspective is max(vals) + 1 (itself).
            if slopes:
                max_points = max(max_points, max(slopes.values()) + 1)
                
        return max_points
```

---

## 5. Complexity
-   **Time**: $O(N^2)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`[[1,1], [2,2], [3,3]]`.
1.  `i=0 (1,1)`.
    -   `j=1 (2,2)`. `dy=1, dx=1`. Slope `(1,1)`. Count 1.
    -   `j=2 (3,3)`. `dy=2, dx=2`. GCD 2. Slope `(1,1)`. Count 2.
    -   Max for P0 = 2 + 1 = 3.
2.  `i=1 (2,2)`.
    -   `j=2 (3,3)`. Slope `(1,1)`. Count 1.
    -   Max = 2.
Result 3.
