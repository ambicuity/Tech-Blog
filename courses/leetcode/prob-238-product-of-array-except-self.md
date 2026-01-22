---
layout: page
title: "238. Product of Array Except Self"
permalink: /courses/leetcode/prob-238-product-of-array-except-self/
---

# 238. Product of Array Except Self

## 1. The Question
Given an integer array `nums`, return an array `answer` such that `answer[i]` is equal to the product of all the elements of `nums` except `nums[i]`.

The product of any prefix or suffix of `nums` is **guaranteed** to fit in a **32-bit** integer.

You must write an algorithm that runs in $O(n)$ time and without using the division operation.

### Example 1
**Input**: `nums = [1,2,3,4]`
**Output**: `[24,12,8,6]`
**Explanation**:
- For index 0: 2*3*4 = 24
- For index 1: 1*3*4 = 12
- For index 2: 1*2*4 = 8
- For index 3: 1*2*3 = 6

### Example 2
**Input**: `nums = [-1,1,0,-3,3]`
**Output**: `[0,0,9,0,0]`

---

## 2. Explanation
If we could use division, we would just calculate `total_product` and for each element return `total_product / nums[i]`. However, this fails if there are zeros (division by zero) and the question explicitly restricts it.

### Approach: Prefix and Suffix Products
To find the product of all except `nums[i]`, we need:
`(Product of everything to left) * (Product of everything to right)`

We can do this in two passes:
1.  **Left Pass**: Calculate the product of all elements to the *left* of each index. Store this in the `answer` array.
2.  **Right Pass**: Maintain a running `suffix_product`. Multiply the `answer[i]` (which currently holds numbers to the left) by this `suffix_product` (which holds numbers to the right).

-   **Time**: $O(n)$
-   **Space**: $O(1)$ (ignoring the output array).

---

## 3. Pseudo Code
```text
n = length(nums)
b = array of size n (answer)

# First pass: Left Products
b[0] = 1
For i from 1 to n-1:
    b[i] = b[i-1] * nums[i-1]

# Second pass: Right Products
R = 1
For i from n-1 down to 0:
    b[i] = b[i] * R
    R = R * nums[i]

Return b
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        n = len(nums)
        answer = [0] * n
        
        # 1. Calculate Left Products
        # answer[i] will contain product of nums[0]...nums[i-1]
        answer[0] = 1
        for i in range(1, n):
            answer[i] = answer[i-1] * nums[i-1]
            
        # 2. Multiply by Right Products
        # R will keep track of product of numbers to the right
        R = 1
        for i in range(n - 1, -1, -1):
            answer[i] = answer[i] * R
            R *= nums[i]
            
        return answer
```

---

## 5. Complexity
-   **Time**: $O(n)$. Two linear scans.
-   **Space**: $O(1)$ extra space (the output array doesn't count towards space complexity).

## 6. Example Walkthrough
`nums = [1, 2, 3, 4]`

**Pass 1 (Left)**:
-   `i=0`: `[1, 0, 0, 0]` (Base case)
-   `i=1`: `1 * 1 = 1`. `[1, 1, 0, 0]`
-   `i=2`: `1 * 2 = 2`. `[1, 1, 2, 0]`
-   `i=3`: `2 * 3 = 6`. `[1, 1, 2, 6]`
Result of Pass 1: `[1, 1, 2, 6]` (Prefix products)

**Pass 2 (Right)**:
-   `i=3`: `ans[3] = 6 * 1 = 6`. `R = 1 * 4 = 4`.
-   `i=2`: `ans[2] = 2 * 4 = 8`. `R = 4 * 3 = 12`.
-   `i=1`: `ans[1] = 1 * 12 = 12`. `R = 12 * 2 = 24`.
-   `i=0`: `ans[0] = 1 * 24 = 24`. `R = 24 * 1 = 24`.

Final: `[24, 12, 8, 6]`.
