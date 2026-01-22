---
layout: page
title: "219. Contains Duplicate II"
permalink: /courses/leetcode/prob-219-contains-duplicate-ii/
---

# 219. Contains Duplicate II

## 1. The Question
Given an integer array `nums` and an integer `k`, return `true` if there are two **distinct indices** `i` and `j` in the array such that `nums[i] == nums[j]` and `abs(i - j) <= k`.

### Example 1
**Input**: `nums = [1,2,3,1], k = 3`
**Output**: `true`

### Example 2
**Input**: `nums = [1,0,1,1], k = 1`
**Output**: `true`

### Example 3
**Input**: `nums = [1,2,3,1,2,3], k = 2`
**Output**: `false`

---

## 2. Explanation
We need to find if any element repeats within a window of size `k`.
Or, simply put, for any duplicate pair, is the difference in indices `<= k`?

### Approach: Hash Map (Sliding Window)
Maintain a map `last_seen[num] -> index`.
As we iterate `i` through `nums`:
1.  If `nums[i]` is in `last_seen`:
    -   Check if `i - last_seen[nums[i]] <= k`.
    -   If yes, return True.
    -   If no, update `last_seen[nums[i]] = i` (we want the closest previous occurrence to check the condition).
2.  `last_seen[nums[i]] = i`.

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
map = {}

For i, num in enumerate(nums):
    if num in map:
        if i - map[num] <= k:
            Return True
    map[num] = i

Return False
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def containsNearbyDuplicate(self, nums: list[int], k: int) -> bool:
        last_seen = {}
        
        for i, num in enumerate(nums):
            if num in last_seen:
                if i - last_seen[num] <= k:
                    return True
            
            # Update the latest index of this number
            last_seen[num] = i
            
        return False
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`nums = [1, 2, 3, 1, 2, 3], k = 2`

1.  `i=0, v=1`. Map={1:0}.
2.  `i=1, v=2`. Map={1:0, 2:1}.
3.  `i=2, v=3`. Map={1:0, 2:1, 3:2}.
4.  `i=3, v=1`. In map at idx 0. $3-0=3$. `3 > 2`. Condition fails. Update Map={1:3...}
5.  `i=4, v=2`. In map at idx 1. $4-1=3$. `3 > 2`. Condition fails.
6.  `i=5, v=3`. In map at idx 2. $5-2=3$. `3 > 2`. Condition fails.
Return False.
