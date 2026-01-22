---
layout: page
title: "11. Container With Most Water"
permalink: /courses/leetcode/prob-11-container-with-most-water/
---

# 11. Container With Most Water

## 1. The Question
You are given an integer array `height` of length `n`. There are `n` vertical lines drawn such that the two endpoints of the `i`th line are `(i, 0)` and `(i, height[i])`.

Find two lines that together with the x-axis form a container, such that the container contains the most water.

Return the maximum amount of water a container can store.

### Example 1
**Input**: `height = [1,8,6,2,5,4,8,3,7]`
**Output**: `49`
**Explanation**: The above vertical lines are represented by array `[1,8,6,2,5,4,8,3,7]`. In this case, the max area of water (blue section) the container can contain is 49. (Between index 1 (height 8) and index 8 (height 7): Width 7, Height min(8,7)=7. Area 49).

### Example 2
**Input**: `height = [1,1]`
**Output**: `1`

---

## 2. Explanation
`Area = min(height[left], height[right]) * (right - left)`

We want to maximize this Area.
-   Width starts at maximum (`n-1`).
-   We want to check if shrinking the width can give us a large enough height increase to produce a larger area.

### Approach: Two Pointers (Greedy)
1.  Start with `left=0` and `right=n-1` (Max width).
2.  Calculate current area. Update max.
3.  **Key Decision**: Which pointer to move?
    -   The area is limited by the **shorter** line.
    -   If we move the taller line inward, the width decreases, and the new height is *at best* the same as the old shorter line. So area is guaranteed to decrease or stay same.
    -   Therefore, to potentially find a larger area, we **must** try to find a taller line to replace the current shorter line.
    -   **Move the pointer pointing to the smaller height.**

-   **Time**: $O(n)$
-   **Space**: $O(1)$

---

## 3. Pseudo Code
```text
left = 0
right = length(height) - 1
max_area = 0

While left < right:
    h = min(height[left], height[right])
    w = right - left
    max_area = max(max_area, h * w)
    
    If height[left] < height[right]:
        left++
    Else:
        right--

Return max_area
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def maxArea(self, height: list[int]) -> int:
        left = 0
        right = len(height) - 1
        max_area = 0
        
        while left < right:
            # Calculate current area
            current_h = min(height[left], height[right])
            current_w = right - left
            max_area = max(max_area, current_h * current_w)
            
            # Greedy choice: Move the shorter line
            # Because moving the taller line can only result in smaller area (less width, same height restriction)
            if height[left] < height[right]:
                left += 1
            else:
                right -= 1
                
        return max_area
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`height = [1, 8, 6, 2, 5, 4, 8, 3, 7]`

1.  `L=0 (1)`, `R=8 (7)`. `Area = min(1,7) * 8 = 8`.
    -   `1 < 7`. Move `L` to 1.
2.  `L=1 (8)`, `R=8 (7)`. `Area = min(8,7) * 7 = 49`. Max=49.
    -   `8 > 7`. Move `R` to 7.
3.  `L=1 (8)`, `R=7 (3)`. `Area = min(8,3) * 6 = 18`. Max=49.
    -   `8 > 3`. Move `R` to 6.
4.  `...`
