---
layout: page
title: "128. Longest Consecutive Sequence"
permalink: /courses/leetcode/prob-128-longest-consecutive-sequence/
---

# 128. Longest Consecutive Sequence

## 1. The Question
Given an unsorted array of integers `nums`, return the length of the longest consecutive elements sequence.

You must write an algorithm that runs in `O(n)` time.

### Example 1
**Input**: `nums = [100,4,200,1,3,2]`
**Output**: `4`
**Explanation**: The longest consecutive elements sequence is `[1, 2, 3, 4]`. Therefore its length is 4.

### Example 2
**Input**: `nums = [0,3,7,2,5,8,4,6,0,1]`
**Output**: `9`

---

## 2. Explanation
We need to find a sequence like `x, x+1, x+2, ...`.
The sort-based approach takes $O(N \log N)$. We need $O(N)$.

### Approach: Hash Set
Put all numbers in a Set for $O(1)$ lookups.
Iterate through the set. For each number `num`:
1.  Check if `num - 1` exists in the set.
    -   If yes, then `num` is NOT the start of a sequence. Skip it.
    -   If no, then `num` IS the start of a sequence.
2.  If it is the start, increment `current_num` while `current_num + 1` is in the set. Count the length.
3.  Update global max.

-   **Time**: $O(N)$. Although we have a while loop inside, each number is visited at most twice (once in outer loop, once in inner "sequence building" loop).
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
num_set = Set(nums)
longest = 0

For num in num_set:
    # Check if num is the start of a sequence
    If (num - 1) not in num_set:
        current_num = num
        current_streak = 1
        
        While (current_num + 1) in num_set:
            current_num += 1
            current_streak += 1
            
        longest = max(longest, current_streak)

Return longest
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def longestConsecutive(self, nums: list[int]) -> int:
        num_set = set(nums)
        longest_streak = 0
        
        for num in num_set:
            # Check if this num is the start of a sequence
            if (num - 1) not in num_set:
                current_num = num
                current_streak = 1
                
                while (current_num + 1) in num_set:
                    current_num += 1
                    current_streak += 1
                    
                longest_streak = max(longest_streak, current_streak)
                
        return longest_streak
```

---

## 5. Complexity
-   **Time**: $O(N)$. Each number is processed as part of a sequence build at most once.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`nums = [100, 4, 200, 1, 3, 2]`
Set = `{1, 2, 3, 4, 100, 200}`

1.  `100`. `99` not in set. Start!
    -   `101` in set? No. Streak: 1.
2.  `4`. `3` in set. Not start. Skip.
3.  `200`. `199` not in set. Start!
    -   `201` in set? No. Streak: 1.
4.  `1`. `0` not in set. Start!
    -   `2` in set? Yes.
    -   `3` in set? Yes.
    -   `4` in set? Yes.
    -   `5` in set? No. Streak: 4.
5.  `3`. `2` in set. Skip.
6.  `2`. `1` in set. Skip.

Max Streak: 4.
