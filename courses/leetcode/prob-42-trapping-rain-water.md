---
layout: page
title: "42. Trapping Rain Water"
permalink: /courses/leetcode/prob-42-trapping-rain-water/
---

# 42. Trapping Rain Water

## 1. The Question
Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, compute how much water it can trap after raining.

### Example 1
**Input**: `height = [0,1,0,2,1,0,1,3,2,1,2,1]`
**Output**: `6`

---

## 2. Explanation
**Two Pointers**.
Maintain `left` and `right` pointers.
Maintain `left_max` and `right_max`.
Move the pointer with the smaller height.
If `height[left] < height[right]`:
-   If `height[left] >= left_max`, update `left_max`.
-   Else `water += left_max - height[left]`.
-   `left++`.
Else:
-   If `height[right] >= right_max`, update `right_max`.
-   Else `water += right_max - height[right]`.
-   `right--`.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
l, r = 0, n-1
l_max, r_max = 0, 0
ans = 0
while l < r:
    if height[l] < height[r]:
        if height[l] >= l_max: l_max = height[l]
        else: ans += l_max - height[l]
        l++
    else:
        if height[r] >= r_max: r_max = height[r]
        else: ans += r_max - height[r]
        r--
return ans
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def trap(self, height: list[int]) -> int:
        if not height:
            return 0
            
        left, right = 0, len(height) - 1
        left_max, right_max = 0, 0
        water = 0
        
        while left < right:
            if height[left] < height[right]:
                if height[left] >= left_max:
                    left_max = height[left]
                else:
                    water += left_max - height[left]
                left += 1
            else:
                if height[right] >= right_max:
                    right_max = height[right]
                else:
                    water += right_max - height[right]
                right -= 1
                
        return water
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[0,1,0,2...]`
1.  `l=0(0), r=11(1)`. `0 < 1`. `l_max=0`. `l=1`.
2.  `l=1(1), r=11(1)`. `1 >= 1` (Else branch). `r_max=1`. `r=10`.
...
Correctly fills valleys.
