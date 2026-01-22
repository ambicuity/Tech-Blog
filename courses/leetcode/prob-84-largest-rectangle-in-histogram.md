---
layout: page
title: "84. Largest Rectangle in Histogram"
permalink: /courses/leetcode/prob-84-largest-rectangle-in-histogram/
---

# 84. Largest Rectangle in Histogram

## 1. The Question
Given an array of integers `heights` representing the histogram's bar height where the width of each bar is `1`, return the area of the largest rectangle in the histogram.

### Example 1
**Input**: `heights = [2,1,5,6,2,3]`
**Output**: `10`
**Explanation**: The largest rectangle has an area = 10 units. (bars 5 and 6, min height 5, width 2).

---

## 2. Explanation
**Monotonic Stack**.
We maintain a stack of indices with increasing heights.
When we encounter a bar `h` smaller than `stack.top()`:
-   It means the rectangle defined by `stack.top()` cannot extend to the right anymore.
-   We pop `top`.
-   `height = heights[top]`.
-   `width = current_index - stack.peek() - 1`. (If stack empty, width = current_index).
-   `area = height * width`.
-   Update max area.
-   Repeat until stack is empty or top <= h.
-   Push `current_index`.

Append a `0` height at end to flush the stack.

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
stack = [-1]
heights.append(0)
ans = 0
for i in 0..len(heights):
    while stack[-1] != -1 and heights[stack[-1]] >= heights[i]:
        h = heights[stack.pop()]
        w = i - stack[-1] - 1
        ans = max(ans, h * w)
    stack.append(i)
return ans
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def largestRectangleArea(self, heights: list[int]) -> int:
        stack = [] # Stores indices
        max_area = 0
        n = len(heights)
        
        # Iterate through all bars
        # Note: We go up to n (inclusive) to handle the 'flush' logic 
        # normally done by appending 0, but can be done implicitly/explicitly.
        # Explicit append is cleaner.
        
        heights.append(0) 
        
        for i, h in enumerate(heights):
            start = i
            while stack and heights[stack[-1]] >= h:
                idx = stack.pop()
                height = heights[idx]
                width = i if not stack else i - stack[-1] - 1
                max_area = max(max_area, height * width)
            
            stack.append(i)
            
        return max_area
```

---

## 5. Complexity
-   **Time**: $O(N)$. Each element pushed/popped once.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`[2, 1, 5, 6, 2, 3] + [0]`.
1.  `2`. Stack `[0]`.
2.  `1`. `1 < 2`. Pop `0` (val 2). Area `2 * (1 - (-1) - 1)` (assume -1 base)?
    -   My code assumes stack empty check.
    -   Pop `0`. Stack empty. Width `1`. Area `2`.
    -   Push `1`. Stack `[1]`.
3.  `5`. `5 >= 1`. Push `2`. `[1, 2]`.
4.  `6`. Push `3`. `[1, 2, 3]`.
5.  `2`. `2 < 6`. Pop `3` (6). Width `4 - 2 - 1 = 1`. Area 6.
    -   `2 < 5`. Pop `2` (5). Width `4 - 1 - 1 = 2`. Area 10. Max 10.
    -   `2 >= 1`. Stop. Push `4`. `[1, 4]`.
...
Final area 10.
