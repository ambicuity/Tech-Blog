---
layout: page
title: "373. Find K Pairs with Smallest Sums"
permalink: /courses/leetcode/prob-373-find-k-pairs-with-smallest-sums/
---

# 373. Find K Pairs with Smallest Sums

## 1. The Question
You are given two integer arrays `nums1` and `nums2` sorted in **non-decreasing order** and an integer `k`.

Define a pair `(u, v)` which consists of one element from the first array and one element from the second array.

Return the `k` pairs `(u1, v1), (u2, v2), ..., (uk, vk)` with the smallest sums.

### Example 1
**Input**: `nums1 = [1,7,11], nums2 = [2,4,6], k = 3`
**Output**: `[[1,2],[1,4],[1,6]]`
**Explanation**: The first 3 pairs are returned from the sequence: [1,2],[1,4],[1,6],[7,2],[7,4],[11,2],[7,6],[11,4],[11,6]

### Example 2
**Input**: `nums1 = [1,1,2], nums2 = [1,2,3], k = 2`
**Output**: `[[1,1],[1,1]]`

---

## 2. Explanation
This is similar to "Merge k Sorted Lists".
We have potentially `N` sorted lists (rows).
Row `i`: `(nums1[i], nums2[0]), (nums1[i], nums2[1]), ...`
Since `nums2` is sorted, each "row" is sorted by sum.

Algorithm:
1.  Initialize Min-Heap with the first pair of each "row": `(nums1[i] + nums2[0], i, 0)` for all `i`.
    -   Optimization: Only push first `min(k, len(nums1))` rows, because elements further down start larger.
2.  Pop smallest sum `(sum, i, j)`. Add pair to result.
3.  Push next element in that "row": `(nums1[i] + nums2[j+1], i, j+1)` if `j+1 < len(nums2)`.
4.  Repeat `k` times.

-   **Time**: $O(k \log k)$. Initial heap size is approx `k` (or `nums1`). Each op is $\log k$.
-   **Space**: $O(k)$.

---

## 3. Pseudo Code
```text
heap = []
for i in range(min(k, len(nums1))):
    heappush(heap, (nums1[i] + nums2[0], i, 0))

res = []
while heap and len(res) < k:
    s, i, j = heappop(heap)
    res.append([nums1[i], nums2[j]])
    
    if j + 1 < len(nums2):
        heappush(heap, (nums1[i] + nums2[j+1], i, j+1))

return res
```

---

## 4. Optimal Code (Python)

```python
import heapq

class Solution:
    def kSmallestPairs(self, nums1: list[int], nums2: list[int], k: int) -> list[list[int]]:
        if not nums1 or not nums2:
            return []
            
        heap = []
        # Optimization: indices into nums1 are 0 to min(k, len(nums1))
        # because the (k+1)-th element of nums1 paired with nums2[0] is surely larger than the k-th pair found so far?
        # Actually, we just need to seed the heap.
        for i in range(min(len(nums1), k)):
            heapq.heappush(heap, (nums1[i] + nums2[0], i, 0))
            
        result = []
        while heap and len(result) < k:
            s, i, j = heapq.heappop(heap)
            result.append([nums1[i], nums2[j]])
            
            # If there is a next element in nums2 for this specific element in nums1
            if j + 1 < len(nums2):
                heapq.heappush(heap, (nums1[i] + nums2[j+1], i, j + 1))
                
        return result
```

---

## 5. Complexity
-   **Time**: $O(k \log k)$.
-   **Space**: $O(k)$.

## 6. Example Walkthrough
`[1,7,11]`, `[2,4,6]`, `k=3`.
1.  Init Heap: `[(3, 0, 0), (9, 1, 0), (13, 2, 0)]`. (Sums: 1+2, 7+2, 11+2).
2.  Pop `(3, 0, 0)`. Res `[[1,2]]`. Push `(1+4=5, 0, 1)`. Heap `[(5,0,1), (9,1,0), (13,2,0)]`.
3.  Pop `(5, 0, 1)`. Res `[[1,2], [1,4]]`. Push `(1+6=7, 0, 2)`. Heap `[(7,0,2), (9,1,0), ...`.
4.  Pop `(7, 0, 2)`. Res `[[1,2], [1,4], [1,6]]`. Done.
