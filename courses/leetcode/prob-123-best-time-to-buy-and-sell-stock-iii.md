---
layout: page
title: "123. Best Time to Buy and Sell Stock III"
permalink: /courses/leetcode/prob-123-best-time-to-buy-and-sell-stock-iii/
---

# 123. Best Time to Buy and Sell Stock III

## 1. The Question
You are given an array `prices` where `prices[i]` is the price of a given stock on the `i`th day.

Find the maximum profit you can achieve. You may complete **at most two transactions**.

Note: You may not engage in multiple transactions simultaneously (i.e., you must sell the stock before you buy again).

### Example 1
**Input**: `prices = [3,3,5,0,0,3,1,4]`
**Output**: `6`
**Explanation**: Buy on day 4 (price = 0) and sell on day 6 (price = 3), profit = 3-0 = 3.
Then buy on day 7 (price = 1) and sell on day 8 (price = 4), profit = 4-1 = 3.

---

## 2. Explanation
We need to track 4 states for each day:
1.  `buy1`: Max profit after buying first stock. (Usually negative e.g. `-price`).
2.  `sell1`: Max profit after selling first stock.
3.  `buy2`: Max profit after buying second stock (after `sell1`).
4.  `sell2`: Max profit after selling second stock (after `buy2`).

Transitions for price `p`:
-   `buy1 = max(buy1, -p)`
-   `sell1 = max(sell1, buy1 + p)`
-   `buy2 = max(buy2, sell1 - p)`
-   `sell2 = max(sell2, buy2 + p)`

Result: `sell2`.

-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
buy1, buy2 = -inf, -inf
sell1, sell2 = 0, 0
for p in prices:
    buy1 = max(buy1, -p)
    sell1 = max(sell1, buy1 + p)
    buy2 = max(buy2, sell1 - p)
    sell2 = max(sell2, buy2 + p)
return sell2
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        # Initialize costs as -infinity (effectively)
        # However, for first buy, max(-inf, -p) will just be -p.
        buy1 = float('-inf')
        sell1 = 0
        buy2 = float('-inf')
        sell2 = 0
        
        for p in prices:
            # Order matters less here because we update based on "prev" state
            # but usually we want to depend on prev iteration.
            # However, updating in sequence "buy1 -> sell1 -> buy2 -> sell2" works 
            # because "buying and selling on same day" (0 profit) is allowed and handled.
            
            buy1 = max(buy1, -p)         # Max profit after 1st buy
            sell1 = max(sell1, buy1 + p) # Max profit after 1st sell
            buy2 = max(buy2, sell1 - p)  # Max profit after 2nd buy
            sell2 = max(sell2, buy2 + p) # Max profit after 2nd sell
            
        return sell2
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`[3,3,5,0,0,3,1,4]`
1.  `3`. `b1=-3`, `s1=0`, `b2=-3`, `s2=0`.
2.  `3`. Same.
3.  `5`. `b1=-3`, `s1=2`, `b2=-3`, `s2=2`.
4.  `0`. `b1=0` (better buy), `s1=2`, `b2=2`, `s2=2`.
5.  `0`. Same.
6.  `3`. `b1=0`, `s1=3`, `b2=2`, `s2=5` (`2+3`).
7.  `1`. `b1=0`, `s1=3`, `b2=2`, `s2=5`.
8.  `4`. `b1=0`, `s1=4` (`0+4`), `b2=2`, `s2=6`.
Result 6.
