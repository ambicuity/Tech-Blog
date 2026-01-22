---
layout: page
title: "56. Merge Intervals"
permalink: /courses/leetcode/prob-56-merge-intervals/
---

# 56. Merge Intervals

## 1. The Question
Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.

### Example 1
**Input**: `intervals = [[1,3],[2,6],[8,10],[15,18]]`
**Output**: `[[1,6],[8,10],[15,18]]`
**Explanation**: Since intervals `[1,3]` and `[2,6]` overlap, merge them into `[1,6]`.

### Example 2
**Input**: `intervals = [[1,4],[4,5]]`
**Output**: `[[1,5]]`
**Explanation**: Intervals `[1,4]` and `[4,5]` are considered overlapping.

---

## 2. Explanation
To merge intervals, we must process them in order.
1.  **Sort** intervals by start time.
2.  Iterate. Keep a `current_interval`.
3.  For `next_interval`:
    -   If `next.start <= current.end`, they overlap. Merge them: `current.end = max(current.end, next.end)`.
    -   If `next.start > current.end`, they don't overlap. Add `current` to result, set `current = next`.

-   **Time**: $O(N \log N)$ due to sorting.
-   **Space**: $O(N)$ for sorting output.

---

## 3. Pseudo Code
```text
Sort intervals by x[0]
res = []
current = intervals[0]

For next in intervals[1...n]:
    if next.start <= current.end:
        current.end = max(current.end, next.end)
    else:
        res.append(current)
        current = next

res.append(current)
Return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        if not intervals:
            return []
            
        # 1. Sort by start time
        intervals.sort(key=lambda x: x[0])
        
        merged = []
        current_start, current_end = intervals[0]
        
        for i in range(1, len(intervals)):
            next_start, next_end = intervals[i]
            
            # If overlapping
            if next_start <= current_end:
                current_end = max(current_end, next_end)
            else:
                # Disjoint, add previous interval
                merged.append([current_start, current_end])
                current_start, current_end = next_start, next_end
                
        # Add the last interval
        merged.append([current_start, current_end])
        
        return merged
```

---

## 5. Complexity
-   **Time**: $O(N \log N)$. Sorting dominates.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`[[1,3], [2,6], [8,10], [15,18]]` (Already sorted)

1.  Current: `[1,3]`.
2.  Next: `[2,6]`. `2 <= 3`. Merge.
    -   New End: `max(3, 6) = 6`. Current: `[1,6]`.
3.  Next: `[8,10]`. `8 > 6`. No Overlap.
    -   Add `[1,6]` to res.
    -   Current: `[8,10]`.
4.  Next: `[15,18]`. `15 > 10`. No Overlap.
    -   Add `[8,10]`.
    -   Current: `[15,18]`.
5.  End loop. Add `[15,18]`.

Result: `[[1,6], [8,10], [15,18]]`.
