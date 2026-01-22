---
layout: page
title: "239. Sliding Window Maximum"
permalink: /courses/leetcode/prob-239-sliding-window-maximum/
---

# 239. Sliding Window Maximum

## 1. The Question
You are given an array of integers `nums`, there is a sliding window of size `k` which is moving from the very left of the array to the very right. You can only see the `k` numbers in the window. Each time the sliding window moves right by one position.

Return the max sliding window.

### Example 1
**Input**: `nums = [1,3,-1,-3,5,3,6,7], k = 3`
**Output**: `[3,3,5,5,6,7]`

---

## 2. Explanation
**Monotonic Deque** (Decreasing).
We need to access the max element of the current window in $O(1)$.
We maintain a deque of **indices** such that their values are in decreasing order.
When we move right (`i`):
1.  Remove indices from back that have `nums[back] <= nums[i]`. (They are useless, as `nums[i]` is newer and larger).
2.  Push `i`.
3.  Remove indices from front that are out of window (`val < i - k + 1`).
4.  Front is the max.

-   **Time**: $O(N)$. Each element pushed/popped once.
-   **Space**: $O(K)$.

---

## 3. Pseudo Code
```text
q = deque()
res = []
for i in 0..n:
    while q and nums[q[-1]] <= nums[i]: q.pop()
    q.append(i)
    if q[0] <= i - k: q.popleft()
    if i >= k - 1: res.append(nums[q[0]])
return res
```

---

## 4. Optimal Code (Python)

```python
from collections import deque

class Solution:
    def maxSlidingWindow(self, nums: list[int], k: int) -> list[int]:
        dq = deque()
        result = []
        
        for i, num in enumerate(nums):
            # Remove smaller elements from the back
            while dq and nums[dq[-1]] <= num:
                dq.pop()
            
            dq.append(i)
            
            # Remove element from the front if it's outside the window
            if dq[0] <= i - k:
                dq.popleft()
                
            # Add to result (starting from when first window is formed)
            if i >= k - 1:
                result.append(nums[dq[0]])
                
        return result
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(K)$.

## 6. Example Walkthrough
`[1,3,-1]`, k=3.
1.  `1`. Deque `[0]`.
2.  `3`. `3 > 1`. Pop `0`. Deque `[1]`.
3.  `-1`. `-1 < 3`. Deque `[1, 2]`.
4.  `i=2 >= 2`. Max `nums[1] = 3`.
5.  ...
