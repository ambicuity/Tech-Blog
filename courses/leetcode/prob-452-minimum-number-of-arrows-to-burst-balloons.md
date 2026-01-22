---
layout: page
title: "452. Minimum Number of Arrows to Burst Balloons"
permalink: /courses/leetcode/prob-452-arrows-balloons/
---

# 452. Minimum Number of Arrows to Burst Balloons

## 1. The Question
There are some spherical balloons taped onto a flat wall that represents the XY-plane. The balloons are represented as a 2D integer array `points` where `points[i] = [xstart, xend]` denotes a balloon whose horizontal diameter stretches between `xstart` and `xend`. You do not know the exact y-coordinates of the balloons.

Arrows can be shot up directly vertically (in the positive y-direction) from different points along the x-axis. A balloon with `xstart` and `xend` is burst by an arrow shot at `x` if `xstart <= x <= xend`. There is no limit to the number of arrows that can be shot. A shot arrow keeps traveling up infinitely, bursting any balloons in its path.

Given the array `points`, return the **minimum number of arrows** that must be shot to burst all balloons.

### Example 1
**Input**: `points = [[10,16],[2,8],[1,6],[7,12]]`
**Output**: `2`
**Explanation**: The balloons can be burst by 2 arrows:
- Shoot an arrow at x = 6, bursting the balloons [2,8] and [1,6].
- Shoot an arrow at x = 11, bursting the balloons [10,16] and [7,12].

### Example 2
**Input**: `points = [[1,2],[3,4],[5,6],[7,8]]`
**Output**: `4`

---

## 2. Explanation
We want to find the minimum set of overlapping regions.
This is a greedy problem. To maximize the number of balloons popped by a single arrow, we should shoot at the **end** of the current balloon's interval.

### Approach: Sort by End Coordinate
1.  Sort the balloons by their **end coordinate**.
2.  Shoot an arrow at the end of the first balloon (`current_end`).
3.  Iterate through the rest.
4.  If a balloon starts *after* `current_end`, our arrow missed it.
    -   We MUST shoot another arrow.
    -   Shoot it at the end of this new balloon. Update `current_end`.
5.  If a balloon starts *before or at* `current_end`, it is already popped by the current arrow (since we shot at `current_end` and `start <= current_end <= end`).

-   **Time**: $O(N \log N)$ (sorting).
-   **Space**: $O(N)$ or $O(\log N)$ (sorting).

---

## 3. Pseudo Code
```text
Sort points by point[1]
arrows = 1
current_end = points[0][1]

For i from 1 to n-1:
    if points[i][0] > current_end:
        arrows++
        current_end = points[i][1]

Return arrows
```

### Why Sort by End?
If we sort by start, we might pick a balloon that ends very late `[1, 100]` first, but that doesn't help us decide where to shoot to pop `[2,3]`.
By sorting by end, we guarantee that the first arrow is placed as far right as possible while still popping the first balloon (which ends earliest). This maximizes the chance of hitting subsequent balloons.

---

## 4. Optimal Code (Python)

```python
class Solution:
    def findMinArrowShots(self, points: list[list[int]]) -> int:
        if not points:
            return 0
            
        # Sort by end coordinate
        points.sort(key=lambda x: x[1])
        
        arrows = 1
        current_end = points[0][1]
        
        for i in range(1, len(points)):
            # If the next balloon starts after the current arrow position
            if points[i][0] > current_end:
                arrows += 1
                current_end = points[i][1]
                
        return arrows
```

---

## 5. Complexity
-   **Time**: $O(N \log N)$.
-   **Space**: $O(N)$ (timsort).

## 6. Example Walkthrough
`[[10,16],[2,8],[1,6],[7,12]]`

1.  Sort by end: `[[1,6], [2,8], [7,12], [10,16]]`.
2.  Balloon `[1,6]`. Shoot at `6`. `Arrows=1`.
3.  Balloon `[2,8]`. `Start(2) <= 6`. Popped.
4.  Balloon `[7,12]`. `Start(7) > 6`. Missed.
    -   Shoot new arrow at `12`. `Arrows=2`.
5.  Balloon `[10,16]`. `Start(10) <= 12`. Popped.

Result: 2.
