---
layout: page
title: "188. Best Time to Buy and Sell Stock IV"
permalink: /courses/leetcode/prob-188-best-time-to-buy-and-sell-stock-iv/
---

# 188. Best Time to Buy and Sell Stock IV

## 1. The Question
You are given an integer array `prices` where `prices[i]` is the price of a given stock on the `i`th day, and an integer `k`.

Find the maximum profit you can achieve. You may complete **at most k transactions**.

Note: You may not engage in multiple transactions simultaneously (i.e., you must sell the stock before you buy again).

### Example 1
**Input**: `k = 2, prices = [2,4,1]`
**Output**: `2`
**Explanation**: Buy on day 1 (price = 2) and sell on day 2 (price = 4), profit = 4-2 = 2.

### Example 2
**Input**: `k = 2, prices = [3,2,6,5,0,3]`
**Output**: `7`

---

## 2. Explanation
This is the generalized version of Stock III (where k=2).
We need arrays `buy[k+1]` and `sell[k+1]`.
`buy[i]` = max profit after `i`-th buy.
`sell[i]` = max profit after `i`-th sell.

Optimization:
If `k >= len(prices) / 2`, we can do as many transactions as possible (like Stock II), just sum all positive slopes.

-   **Time**: $O(N \cdot K)$.
-   **Space**: $O(K)$.

---

## 3. Pseudo Code
```text
if k >= n/2: return stockII(prices)

buy = [-inf] * (k+1)
sell = [0] * (k+1)

for p in prices:
    for i in 1..k:
        buy[i] = max(buy[i], sell[i-1] - p)
        sell[i] = max(sell[i], buy[i] + p)
return sell[k]
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def maxProfit(self, k: int, prices: list[int]) -> int:
        n = len(prices)
        if n == 0:
            return 0
            
        # Optimization: if k is large enough, just grab all positive diffs
        if k >= n // 2:
            profit = 0
            for i in range(1, n):
                if prices[i] > prices[i-1]:
                    profit += prices[i] - prices[i-1]
            return profit
            
        # DP: k transactions
        buy = [float('-inf')] * (k + 1)
        sell = [0] * (k + 1)
        
        for p in prices:
            for i in range(1, k + 1):
                # buy[i]: buy i-th stock. We use money from (i-1)-th sell.
                buy[i] = max(buy[i], sell[i-1] - p)
                
                # sell[i]: sell i-th stock. 
                sell[i] = max(sell[i], buy[i] + p)
                
        return sell[k]
```

---

## 5. Complexity
-   **Time**: $O(N \cdot K)$.
-   **Space**: $O(K)$.

## 6. Example Walkthrough
`k=2, [3,2,6,5,0,3]`
1.  `3`. `b1=-3, s1=0, b2=-3, s2=0`.
2.  `2`. `b1=-2, s1=0, b2=-2, s2=0`.
3.  `6`. `b1=-2, s1=4, b2=-2, s2=4`.
4.  `5`. `b1=-2, s1=4, b2=-1(4-5), s2=4`. (Buy2 after Sell1: Sell1 was 4. 4-5=-1).
5.  `0`. `b1=0, s1=4, b2=4(4-0), s2=4`.
6.  `3`. `b1=0, s1=4, b2=4, s2=7(4+3)`.
Result 7.
