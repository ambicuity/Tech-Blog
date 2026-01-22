---
layout: page
title: "57. Insert Interval"
permalink: /courses/leetcode/prob-57-insert-interval/
---

# 57. Insert Interval

## 1. The Question
You are given an array of non-overlapping intervals `intervals` where `intervals[i] = [start_i, end_i]` represent the start and the end of the `ith` interval and `intervals` is sorted in ascending order by `start_i`. You are also given an interval `newInterval = [start, end]` that represents the start and end of another interval.

Insert `newInterval` into `intervals` such that `intervals` is still sorted in ascending order by `start_i` and `intervals` still does not have any overlapping intervals (merge overlapping intervals if necessary).

Return `intervals` after the insertion.

### Example 1
**Input**: `intervals = [[1,3],[6,9]], newInterval = [2,5]`
**Output**: `[[1,5],[6,9]]`

### Example 2
**Input**: `intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]`
**Output**: `[[1,2],[3,10],[12,16]]`
**Explanation**: Because the new interval `[4,8]` overlaps with `[3,5]`, `[6,7]`, `[8,10]`.

---

## 2. Explanation
Since the original list is **sorted** and **non-overlapping**, we can do this in one pass.
We have three parts:
1.  Intervals completely **before** the new interval.
2.  Intervals that **overlap** with the new interval (merge them).
3.  Intervals completely **after** the new interval.

Algorithm:
1.  Add all intervals ending before `newInterval` starts.
2.  While intervals overlap with `newInterval`:
    -   Merge them: `newInterval.start = min(old.start, new.start)`, `newInterval.end = max(old.end, new.end)`.
3.  Add the merged `newInterval`.
4.  Add all remaining intervals.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$ (excluding output).

---

## 3. Pseudo Code
```text
res = []
i = 0

# 1. Add intervals before
While i < n and intervals[i].end < newInterval.start:
    res.append(intervals[i])
    i++

# 2. Merge overlapping
While i < n and intervals[i].start <= newInterval.end:
    newInterval.start = min(newInterval.start, intervals[i].start)
    newInterval.end = max(newInterval.end, intervals[i].end)
    i++

res.append(newInterval)

# 3. Add intervals after
While i < n:
    res.append(intervals[i])
    i++

Return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def insert(self, intervals: list[list[int]], newInterval: list[int]) -> list[list[int]]:
        res = []
        i = 0
        n = len(intervals)
        
        # 1. Add all intervals that effectively end before the new interval starts
        while i < n and intervals[i][1] < newInterval[0]:
            res.append(intervals[i])
            i += 1
            
        # 2. Merge all overlapping intervals
        # Condition: interval starts before newInterval ends
        while i < n and intervals[i][0] <= newInterval[1]:
            newInterval[0] = min(newInterval[0], intervals[i][0])
            newInterval[1] = max(newInterval[1], intervals[i][1])
            i += 1
            
        res.append(newInterval)
        
        # 3. Add remaining intervals
        while i < n:
            res.append(intervals[i])
            i += 1
            
        return res
```

---

## 5. Complexity
-   **Time**: $O(N)$. Single pass.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], new = [4,8]`

1.  `[1,2]`. Ends at 2 < 4. Add `[1,2]`.
2.  `[3,5]`. Starts at 3 <= 8. Overlaps!
    -   `new = [min(4,3), max(8,5)] = [3,8]`.
3.  `[6,7]`. Starts at 6 <= 8. Overlaps!
    -   `new = [min(3,6), max(8,7)] = [3,8]`.
4.  `[8,10]`. Starts at 8 <= 8. Overlaps!
    -   `new = [min(3,8), max(8,10)] = [3,10]`.
5.  `[12,16]`. Starts at 12 > 10. Does not overlap.
    -   Add `[3,10]`.
6.  Add remaining: `[12,16]`.

Result: `[[1,2], [3,10], [12,16]]`.
