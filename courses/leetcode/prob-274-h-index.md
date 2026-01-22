---
layout: page
title: "274. H-Index"
permalink: /courses/leetcode/prob-274-h-index/
---

# 274. H-Index

## 1. The Question
Given an array of integers `citations` where `citations[i]` is the number of citations a researcher received for their `i`th paper, return the researcher's h-index.

According to the definition of h-index on Wikipedia: A scientist has an index `h` if `h` of their `n` papers have at least `h` citations each, and the other `n − h` papers have no more than `h` citations each.

### Example 1
**Input**: `citations = [3,0,6,1,5]`
**Output**: `3`
**Explanation**: `[3, 0, 6, 1, 5]` means the researcher has 5 papers with 3, 0, 6, 1, 5 citations respectively.
Since they have 3 papers with at least 3 citations each and the remaining two with no more than 3 citations each, their h-index is 3.

### Example 2
**Input**: `citations = [1,3,1]`
**Output**: `1`

---

## 2. Explanation
We need to find the maximum value `h` such that there are at least `h` papers with $\ge h$ citations.

### Approach 1: Sorting
Sort the citations in descending order.
Iterate through the sorted list. If `citations[i] >= i + 1`, it means we have found at least `i+1` papers with at least `citations[i]` citations (and thus certainly `i+1` citations since `citations[i] >= i+1`).
-   **Time**: $O(n \lg n)$

### Approach 2: Counting Sort (Optimal)
The H-Index cannot exceed the total number of papers `n`.
We can use buckets to count how many papers have `c` citations.
1.  Create an array `buckets` of size `n + 1`.
2.  For each paper, increment `buckets[min(citations[i], n)]`.
3.  Iterate from right to left (from `n` down to `0`). Keep a running `count` of papers.
4.  If `count >= i` (where `i` is current citation count), then `i` is the H-Index.

-   **Time**: $O(n)$
-   **Space**: $O(n)$

---

## 3. Pseudo Code (Counting Sort)
```text
n = length(citations)
buckets = array of size n + 1 (all zeros)

For c in citations:
    If c >= n: buckets[n]++
    Else: buckets[c]++

count = 0
For i from n down to 0:
    count += buckets[i]
    If count >= i:
        Return i

Return 0
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def hIndex(self, citations: list[int]) -> int:
        n = len(citations)
        buckets = [0] * (n + 1)
        
        # Populate buckets
        for c in citations:
            if c >= n:
                buckets[n] += 1
            else:
                buckets[c] += 1
                
        count = 0
        # Iterate from back to find the max h
        for i in range(n, -1, -1):
            count += buckets[i]
            if count >= i:
                return i
                
        return 0
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(n)$ for the buckets.

## 6. Example Walkthrough
`citations = [3, 0, 6, 1, 5]`, `n = 5`

1.  **Buckets**:
    -   `3`: bucket[3]++
    -   `0`: bucket[0]++
    -   `6`: bucket[5]++ (capped at 5)
    -   `1`: bucket[1]++
    -   `5`: bucket[5]++
    `buckets = [1, 1, 0, 1, 0, 2]`  (Indices: 0 to 5)

2.  **Scan Backwards**:
    -   `i=5`: `count = 2`. `2 < 5`.
    -   `i=4`: `count = 2 + 0 = 2`. `2 < 4`.
    -   `i=3`: `count = 2 + 1 = 3`. `3 >= 3`. **Return 3**.

Result: 3.
