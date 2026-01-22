---
layout: page
title: "169. Majority Element"
permalink: /courses/leetcode/prob-169-majority-element/
---

# 169. Majority Element

## 1. The Question
Given an array `nums` of size `n`, return the majority element.
The majority element is the element that appears more than `⌊n / 2⌋` times. You may assume that the majority element always exists in the array.

### Example
**Input**: `nums = [2,2,1,1,1,2,2]`
**Output**: `2`

---

## 2. Explanation
We need to find the "King of the Hill". Because it appears $> n/2$ times, it is more frequent than all other elements combined.

### Approach 1: HashMap
Count frequencies. $O(n)$ Time, $O(n)$ Space.

### Approach 2: Sorting
Sort and take the middle element `nums[n//2]`. $O(n \lg n)$ Time.

### Approach 3: Boyer-Moore Voting Algorithm (Optimal)
Maintain a `candidate` and a `count`.
-   If `count == 0`: set current number as candidate.
-   If num == candidate: count++.
-   Else: count--.
Because majority > all others, it will survive the subtractions.

---

## 3. Pseudo Code
```text
count = 0, candidate = None
For num in nums:
    If count == 0: candidate = num
    If num == candidate: count += 1
    Else: count -= 1
Return candidate
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def majorityElement(self, nums: list[int]) -> int:
        count = 0
        candidate = None
        
        for num in nums:
            if count == 0:
                candidate = num
            
            if num == candidate:
                count += 1
            else:
                count -= 1
        
        return candidate
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[2, 2, 1, 1, 1, 2, 2]`
1.  `2`: `count=1`, `cand=2`
2.  `2`: `count=2`
3.  `1`: `count=1` (Different, decrement)
4.  `1`: `count=0` (Different, decrement)
5.  `1`: `count=1`, `cand=1` (Count was 0, new candidate)
6.  `2`: `count=0`
7.  `2`: `count=1`, `cand=2`.
Result: 2.
