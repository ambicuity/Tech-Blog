---
layout: page
title: "122. Best Time to Buy and Sell Stock II"
permalink: /courses/leetcode/prob-122-best-time-to-buy-and-sell-stock-ii/
---

# 122. Best Time to Buy and Sell Stock II

## 1. The Question
You are given an integer array `prices` where `prices[i]` is the price of a given stock on the `i`th day.

On each day, you may decide to buy and/or sell the stock. You can only hold at most one share of the stock at any time. However, you can buy it then immediately sell it on the same day.

Find and return the maximum profit you can achieve.

### Example 1
**Input**: `prices = [7,1,5,3,6,4]`
**Output**: `7`
**Explanation**:
Buy on day 2 (price = 1) and sell on day 3 (price = 5), profit = 5-1 = 4.
Buy on day 4 (price = 3) and sell on day 5 (price = 6), profit = 6-3 = 3.
Total profit = 4 + 3 = 7.

### Example 2
**Input**: `prices = [1,2,3,4,5]`
**Output**: `4`
**Explanation**: Buy on day 1 (price = 1) and sell on day 5 (price = 5), profit = 5-1 = 4.
Total profit is 4.

---

## 2. Explanation
Unlike the previous problem (Buy Once), here we can trade infinitely. We want to capture **every single increase** in price.

If the price graph goes up from `a` to `b` to `c` (where `a < b < c`), buying at `a` and selling at `c` (`c-a`) gives the same profit as buying at `a`, selling at `b`, buying at `b`, and selling at `c` (`(b-a) + (c-b) = c-a`).

Therefore, we can simply be greedy: **if tomorrow's price is higher than today's, we buy today and sell tomorrow.**

### Strategy
Iterate from Day 1 to Day `n-1`. If `prices[i] > prices[i-1]`, add the difference to `total_profit`.

---

## 3. Pseudo Code
```text
max_profit = 0

For i from 1 to length(prices) - 1:
    If prices[i] > prices[i-1]:
        max_profit += prices[i] - prices[i-1]

Return max_profit
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        max_profit = 0
        
        for i in range(1, len(prices)):
            # If price went up, capture the profit
            if prices[i] > prices[i-1]:
                max_profit += (prices[i] - prices[i-1])
                
        return max_profit
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`prices = [7, 1, 5, 3, 6, 4]`

1.  `i=1` (Price 1): `1 < 7`. No profit.
2.  `i=2` (Price 5): `5 > 1`. Profit += `5-1` (4). Total = 4.
3.  `i=3` (Price 3): `3 < 5`. No profit.
4.  `i=4` (Price 6): `6 > 3`. Profit += `6-3` (3). Total = 4 + 3 = 7.
5.  `i=5` (Price 4): `4 < 6`. No profit.

Total = 7.
