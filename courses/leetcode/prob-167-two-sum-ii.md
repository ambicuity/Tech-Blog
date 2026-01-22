---
layout: page
title: "167. Two Sum II - Input Array Is Sorted"
permalink: /courses/leetcode/prob-167-two-sum-ii/
---

# 167. Two Sum II - Input Array Is Sorted

## 1. The Question
Given a **1-indexed** array of integers `numbers` that is already **sorted in non-decreasing order**, find two numbers such that they add up to a specific `target` number. Let these two numbers be `numbers[index1]` and `numbers[index2]` where `1 <= index1 < index2 <= numbers.length`.

Return the indices of the two numbers, `index1` and `index2`, added by one as an integer array `[index1, index2]` of length 2.

The tests are generated such that there is **exactly one solution**. You may not use the same element twice. Your solution must use only constant extra space.

### Example 1
**Input**: `numbers = [2,7,11,15], target = 9`
**Output**: `[1,2]`
**Explanation**: The sum of 2 and 7 is 9. Therefore, index1 = 1, index2 = 2. We return [1, 2].

### Example 2
**Input**: `numbers = [2,3,4], target = 6`
**Output**: `[1,3]`
**Explanation**: The sum of 2 and 4 is 6. Therefore index1 = 1, index2 = 3. We return [1, 3].

---

## 2. Explanation
Since the array is sorted, we can use the "Two Pointer" technique to find the sum efficiently.

### Approach: Two Pointers (Shrinking Window)
1.  Initialize `left` at 0 (smallest) and `right` at end (largest).
2.  Calculate `sum = numbers[left] + numbers[right]`.
3.  If `sum == target`: Found it! Return `[left+1, right+1]`.
4.  If `sum > target`: We need a smaller sum. The only way to decrease sum is to decrease the larger element. Move `right` to left (right--).
5.  If `sum < target`: We need a larger sum. The only way to increase sum is to increase the smaller element. Move `left` to right (left++).

-   **Time**: $O(n)$
-   **Space**: $O(1)$

---

## 3. Pseudo Code
```text
left = 0
right = length(numbers) - 1

While left < right:
    cur_sum = numbers[left] + numbers[right]
    
    If cur_sum == target:
        Return [left + 1, right + 1]
    
    Else If cur_sum > target:
        right--
    
    Else:
        left++
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def twoSum(self, numbers: list[int], target: int) -> list[int]:
        left = 0
        right = len(numbers) - 1
        
        while left < right:
            current_sum = numbers[left] + numbers[right]
            
            if current_sum == target:
                # 1-indexed result
                return [left + 1, right + 1]
            
            elif current_sum > target:
                # Sum is too big, decrease the larger element
                right -= 1
            
            else:
                # Sum is too small, increase the smaller element
                left += 1
                
        return [] # Should not reach here
```

---

## 5. Complexity
-   **Time**: $O(n)$. Each step we either increment `left` or decrement `right`. Max `n` steps.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`numbers = [2, 7, 11, 15]`, `target = 9`

1.  `L=0 (2)`, `R=3 (15)`. `Sum = 17`.
    -   `17 > 9`. Move R left. `R=2`.
2.  `L=0 (2)`, `R=2 (11)`. `Sum = 13`.
    -   `13 > 9`. Move R left. `R=1`.
3.  `L=0 (2)`, `R=1 (7)`. `Sum = 9`.
    -   `9 == 9`. Return `[1, 2]`.
