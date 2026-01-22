---
layout: page
title: "295. Find Median from Data Stream"
permalink: /courses/leetcode/prob-295-find-median-from-data-stream/
---

# 295. Find Median from Data Stream

## 1. The Question
The **median** is the middle value in an ordered integer list. If the size of the list is even, there is no middle value, and the median is the mean of the two middle values.

Implement the `MedianFinder` class:
-   `MedianFinder()` initializes the object.
-   `void addNum(int num)` adds the integer `num` from the data stream to the data structure.
-   `double findMedian()` returns the median of all elements so far.

### Example 1
**Input**
`["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"]`
`[[], [1], [2], [], [3], []]`
**Output**
`[null, null, null, 1.5, null, 2.0]`

---

## 2. Explanation
To find median efficiently, we need access to the middle elements.
We can maintain two heaps:
1.  **Bottom Half (Max-Heap)**: Stores the smaller half of numbers (e.g., if array is `[1,2,3,4]`, this stores `1,2`).
2.  **Top Half (Min-Heap)**: Stores the larger half of numbers (e.g., `3,4`).

Rules:
-   The two heaps should have equal size, or "Bottom" has 1 more element.
-   `max(Bottom) <= min(Top)`.

Operations:
-   **Add**: Add to Bottom. Then move max(Bottom) to Top. If Top has more elements than Bottom, move min(Top) back to Bottom. (Balancing).
-   **Median**:
    -   If sizes equal: `(max(Bottom) + min(Top)) / 2`.
    -   If unequal (Bottom has 1 more): `max(Bottom`.

-   **Time**: $O(\log N)$ for add, $O(1)$ for find.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
small = [] # Max heap (Bottom)
large = [] # Min heap (Top)

addNum(num):
    heappush(small, -num)
    heappush(large, -heappop(small))
    
    if len(large) > len(small):
        heappush(small, -heappop(large))

findMedian():
    if len(small) > len(large): return -small[0]
    else: return (-small[0] + large[0]) / 2.0
```

---

## 4. Optimal Code (Python)

```python
import heapq

class MedianFinder:

    def __init__(self):
        # Two heaps: 
        # small: max_heap (stores smaller half). Python has min_heap, so store negatives.
        # large: min_heap (stores larger half).
        self.small = []
        self.large = []

    def addNum(self, num: int) -> None:
        # Steps to maintain balance and order property:
        # 1. Add to small, then pop max from small to large.
        #    This ensures the new element finds its correct place relative to the divide.
        heapq.heappush(self.small, -num)
        heapq.heappush(self.large, -heapq.heappop(self.small))
        
        # 2. Re-balance if large is bigger than small.
        #    We want len(small) >= len(large) by at most 1.
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def findMedian(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        else:
            return (-self.small[0] + self.large[0]) / 2.0
```

---

## 5. Complexity
-   **Time**: $O(\log N)$ add, $O(1)$ find.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
1.  Add 1. `Small [-1]`. `Large []`. -> `Small []`, `Large [1]`. -> Balance -> `Small [-1]`, `Large []`.
2.  Add 2. `Small [-1, -2]`. `Large []`. -> Pop -2 -> `Large [2]`. Balance OK. `S[-1], L[2]`.
3.  Median: `(1 + 2) / 2 = 1.5`.
4.  Add 3. `S[-1, -3]`. `L[2]`. -> Max(-1) -> `L[2, 1]`. -> Pop 1 -> `L[1, 2]`.
    -   Balance: `L` has 2, `S` has 1. Move 1 to `S`.
    -   `S[-1, -2]`, `L[3]`. (Wait, let's trace carefully)
    -   Add 3 to `S`(`-3`). `S` is `[-1, -3]`.
    -   Pop max `S` (`-1`) -> push to `L` (`1`). `L` is `[1, 2]`. `S` is `[-3]`.
    -   Len L(2) > Len S(1). Pop min `L` (`1`) -> push to `S` (`-1`).
    -   `S` is `[-1, -3]`. `L` is `[2]`.
    Median: Max S = 2 (Wait, -(-2)=2. Wait, `-1` came from 1. `-3` came from 3. Logic: 1, 3 in S? No.
    Let's restart trace.
    Nums: 1, 2, 3.
    1.  Add 1. `S[-1]`.
    2.  Add 2. `S[-2, -1]`. Pop `-1`(1) to L. `S[-2]`, `L[1]`. Median `(2+1)/2=1.5`.
    3.  Add 3. `S[-2, -3]`. Pop `-2`(2) to L. `S[-3]`, `L[1, 2]`.
        -   L size 2 > S size 1. Pop `1` to S. `S[-3, -1]`. `L[2]`.
    Median: `-small[0]` is `-(-1)=1`. Wait, median of `1,2,3` is 2.
    Why -1 is top? `heapq.heappush` maintains heap property.
    `S` contents `[-1, -3]`. Top is `-1` (largest negative, so smallest magnitude... wait no. `heapq` is min heap. `-3` is smaller than `-1`.)
    Top of S (min-heap of negs) is `-3`? No, `-3 < -1`. So `-3` is root.
    Wait, `heappush(-1)`, `heappush(-2)`. Stack: `[-2, -1]`.
    It seems my manual trace logic of heap structure is failing.
    Correct Logic:
    `S` stores lower half. `L` stores upper half.
    `1, 2, 3`.
    1. `S` gets `1`. Move `1` to `L`. `L=[1]`. `L>S`. Move `1` to `S`. `S=[-1]`, `L=[]`.
    2. `S` gets `2`. `S=[-2, -1]`. Move `-(-1)=1` to `L`. `S=[-2]`, `L=[1]`. Equal. Med 1.5.
    3. `S` gets `3`. `S=[-2, -3]`. Move `-(-2)=2` to `L`. `S=[-3]`, `L=[1, 2]`.
       `L` size 2, `S` size 1. Move `1` to `S`. `S=[-3, -1]`. `L=[2]`.
       Top of `S` is `-3`? No, `-3 < -1`. `-3` is at root. So `max` of lower half is `3`? No.
       `-1` corresponds to `1`. `-3` corresponds to `3`.
       So `S` has `1, 3`? NO. `S` should have `1, 2`. `L` should have `3`.
       Step 3 Again:
       Status: `S=[-2]`(2), `L=[1]`(1). Wait, `S` has `-2`. Max(Lower) is 2. `L` has 1. Min(Upper) is 1. `2 <= 1` False.
       My manual trace failed at Step 2.
       `S` stores **Smaller Half**. `L` stores **Larger Half**.
       Add 2: `S` gets `-2`. `S=[-1, -2]`. Pop smallest of S (`-2`) (which is MAX of positive S... NO).
       Python `heap` is MIN heap.
       `S` stores negatives. `heappop(S)` returns the MOST NEGATIVE number (e.g. -100 vs -1. -100 is smaller).
       So `S` actually acts as a MAX heap for the negative values?
       If I store `-x`, `min(-x)` is `-max(x)`. So `heappop` returns the stored value of the MAX element.
       Correct.
       
       Retrace Step 2:
       `val=2`. `push(S, -2)`. `S=[-2, -1]`. Root is `-2`.
       `pop(S)` -> `-2`. Push `2` to `L`. `L=[2]`.
       `S=[-1]`. `L=[2]`.
       Median: `(-(-1) + 2)/2 = 1.5`. Correct.
       
       Step 3:
       `val=3`. `push(S, -3)`. `S=[-3, -1]`. Root is `-3`.
       `pop(S)` -> `-3`. Push `3` to `L`. `L=[2, 3]`.
       `L` size 2 > `S` size 1.
       Pop `L` (2). Push `-2` to `S`.
       `S=[-2, -1]`. `L=[3]`.
       Top of `S` is `-2`. Max Lower is 2.
       Median is 2. Correct.
