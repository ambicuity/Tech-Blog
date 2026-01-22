---
layout: page
title: "228. Summary Ranges"
permalink: /courses/leetcode/prob-228-summary-ranges/
---

# 228. Summary Ranges

## 1. The Question
You are given a **sorted unique** integer array `nums`.

A **range** `[a,b]` is the set of all integers from `a` to `b` (inclusive).

Return the **smallest sorted list of ranges** that cover all the numbers in the array exactly. That is, each element of `nums` is covered by exactly one of the ranges, and there is no integer `x` such that `x` is in one of the ranges but not in `nums`.

Each range `[a,b]` in the list should be output as:
-   `"a->b"` if `a != b`
-   `"a"` if `a == b`

### Example 1
**Input**: `nums = [0,1,2,4,5,7]`
**Output**: `["0->2","4->5","7"]`
**Explanation**: The ranges are:
[0,2] --> "0->2"
[4,5] --> "4->5"
[7,7] --> "7"

### Example 2
**Input**: `nums = [0,2,3,4,6,8,9]`
**Output**: `["0","2->4","6","8->9"]`

---

## 2. Explanation
We need to group consecutive numbers.
Iterate through the array. Keep track of the start of the current range.
If `nums[i] + 1 != nums[i+1]`, the current range ends.
-   Format it as `start->end` (or `start` if `start==end`).
-   Start a new range at `i+1`.

-   **Time**: $O(N)$. Single pass.
-   **Space**: $O(1)$ (output list not counted).

---

## 3. Pseudo Code
```text
res = []
start = nums[0]

For i from 0 to n-1:
    # If it's the last element OR next element is not consecutive
    If i == n-1 OR nums[i] + 1 != nums[i+1]:
        if start == nums[i]:
            res.append(str(start))
        else:
            res.append(f"{start}->{nums[i]}")
        
        if i != n-1:
            start = nums[i+1]

Return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def summaryRanges(self, nums: list[int]) -> list[str]:
        if not nums:
            return []
            
        ranges = []
        start = nums[0]
        
        for i in range(len(nums)):
            # Check if range ends here
            # Range ends if it's the last element OR next is not consecutive
            if i == len(nums) - 1 or nums[i] + 1 != nums[i+1]:
                if start == nums[i]:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}->{nums[i]}")
                
                # Start new range
                if i != len(nums) - 1:
                    start = nums[i+1]
                    
        return ranges
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`nums = [0, 1, 2, 4, 5, 7]`

1.  `i=0 (0)`. Next is 1. Continue.
2.  `i=1 (1)`. Next is 2. Continue.
3.  `i=2 (2)`. Next is 4. Break!
    -   `start=0`, `end=2`. Add `"0->2"`.
    -   New start = 4.
4.  `i=3 (4)`. Next is 5. Continue.
5.  `i=4 (5)`. Next is 7. Break!
    -   `start=4`, `end=5`. Add `"4->5"`.
    -   New start = 7.
6.  `i=5 (7)`. Last. Break!
    -   `start=7`, `end=7`. Add `"7"`.

Result: `["0->2", "4->5", "7"]`.
