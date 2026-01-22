---
layout: page
title: "135. Candy"
permalink: /courses/leetcode/prob-135-candy/
---

# 135. Candy

## 1. The Question
There are `n` children standing in a line. Each child is assigned a rating value given in the integer array `ratings`.

You are giving candies to these children subjected to the following requirements:
1.  Each child must have at least one candy.
2.  Children with a higher rating than their neighbors get more candies than their neighbors.

Return the minimum number of candies you need to have to distribute the candies to the children.

### Example 1
**Input**: `ratings = [1,0,2]`
**Output**: `5`
**Explanation**: You can allocate to the first, second and third child with 2, 1, 2 candies respectively.

### Example 2
**Input**: `ratings = [1,2,2]`
**Output**: `4`
**Explanation**: You can allocate to the first, second and third child with 1, 2, 1 candies respectively.
The third child gets 1 candy because it satisfies the above two conditions.

---

## 2. Explanation
We need to satisfy conditions relative to both left and right neighbors.

1.  **Left Neighbor Rule**: If `ratings[i] > ratings[i-1]`, then `candies[i] > candies[i-1]`.
2.  **Right Neighbor Rule**: If `ratings[i] > ratings[i+1]`, then `candies[i] > candies[i+1]`.

Trying to satisfy both at simultaneously is tricky. Instead, we can split this into two passes.

### Approach: Two-Pass Greedy
1.  **Left to Right**: Initialize everyone with 1 candy. Iterate from `1` to `n`.
    -   If `ratings[i] > ratings[i-1]`, update `candies[i] = candies[i-1] + 1`.
    -   Otherwise, keep it as 1 (or whatever it is).
2.  **Right to Left**: Iterate from `n-2` to `0`.
    -   If `ratings[i] > ratings[i+1]`, make sure `candies[i]` is larger than `candies[i+1]`.
    -   Update: `candies[i] = max(candies[i], candies[i+1] + 1)`.

Finally, sum up the candies array.

---

## 3. Pseudo Code
```text
n = length(ratings)
candies = array of size n filled with 1

# Pass 1: Left to Right
For i from 1 to n-1:
    If ratings[i] > ratings[i-1]:
        candies[i] = candies[i-1] + 1

# Pass 2: Right to Left
For i from n-2 down to 0:
    If ratings[i] > ratings[i+1]:
        candies[i] = max(candies[i], candies[i+1] + 1)

Return sum(candies)
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def candy(self, ratings: list[int]) -> int:
        n = len(ratings)
        candies = [1] * n
        
        # 1. Forward Pass (Ensure right element > left element if rating higher)
        for i in range(1, n):
            if ratings[i] > ratings[i-1]:
                candies[i] = candies[i-1] + 1
        
        # 2. Backward Pass (Ensure left element > right element if rating higher)
        for i in range(n - 2, -1, -1):
            if ratings[i] > ratings[i+1]:
                candies[i] = max(candies[i], candies[i+1] + 1)
                
        return sum(candies)
```

---

## 5. Complexity
-   **Time**: $O(n)$. Two linear scans + one sum scan.
-   **Space**: $O(n)$ for the candies array. (There is an $O(1)$ space solution using slope counting, but it is much more complex and hard to implement in interview settings).

## 6. Example Walkthrough
`ratings = [1, 0, 2]`

1.  **Init**: `[1, 1, 1]`
2.  **Pass 1 (Left -> Right)**:
    -   `i=1` (0 > 1? No). `[1, 1, 1]`.
    -   `i=2` (2 > 0? Yes). `candies[2] = 1 + 1 = 2`.
    -   Array: `[1, 1, 2]`.
3.  **Pass 2 (Right -> Left)**:
    -   `i=1` (0 > 2? No).
    -   `i=0` (1 > 0? Yes). `candies[0] = max(1, candies[1] + 1) = max(1, 2) = 2`.
    -   Array: `[2, 1, 2]`.

Sum = 5. Correct.
