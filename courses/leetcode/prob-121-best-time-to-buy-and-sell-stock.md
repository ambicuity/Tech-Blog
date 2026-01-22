---
layout: page
title: "121. Best Time to Buy and Sell Stock"
permalink: /courses/leetcode/prob-121-best-time-to-buy-and-sell-stock/
---

# 121. Best Time to Buy and Sell Stock

## 1. The Question
You are given an array `prices` where `prices[i]` is the price of a given stock on the `i`th day.

You want to maximize your profit by choosing a **single day** to buy one stock and choosing a **different day in the future** to sell that stock.

Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return `0`.

### Example 1
**Input**: `prices = [7,1,5,3,6,4]`
**Output**: `5`
**Explanation**: Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.
Note that buying on day 2 and selling on day 1 is not allowed because you must buy before you sell.

### Example 2
**Input**: `prices = [7,6,4,3,1]`
**Output**: `0`
**Explanation**: In this case, no transactions are done and the max profit = 0.

---

## 2. Explanation
To make money, we need to buy low and sell high. We need to find $max(prices[j] - prices[i])$ where $j > i$.

### Approach 1: Brute Force
Check every pair $(i, j)$ with $j > i$.
-   **Time**: $O(n^2)$ - Too slow.

### Approach 2: One Pass (Optimal)
As we move through the array, we just need to know:
1.  What is the **lowest price** I've seen so far? (Potential buying day)
2.  If I sell today, what is my profit? (`current_price - min_price`)

-   Maintain a `min_price` variable (initialized to infinity).
-   Maintain a `max_profit` variable (initialized to 0).
-   Iterate through each price:
    -   If `price < min_price`, update `min_price`.
    -   Else, calculate `profit = price - min_price`. If `profit > max_profit`, update `max_profit`.

---

## 3. Pseudo Code
```text
min_price = infinity
max_profit = 0

For price in prices:
    If price < min_price:
        min_price = price
    Else If (price - min_price) > max_profit:
        max_profit = price - min_price

Return max_profit
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        min_price = float('inf')
        max_profit = 0
        
        for price in prices:
            if price < min_price:
                min_price = price
            elif price - min_price > max_profit:
                max_profit = price - min_price
                
        return max_profit
```

---

## 5. Complexity
-   **Time**: $O(n)$. Single pass.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`prices = [7, 1, 5, 3, 6, 4]`

1.  **Day 1 (7)**:
    -   `min_price` becomes 7.
    -   `max_profit` = 0.
2.  **Day 2 (1)**:
    -   `1 < 7`, so `min_price` becomes 1.
    -   (Can't sell for profit yet).
3.  **Day 3 (5)**:
    -   `5 > 1`. Profit would be `5 - 1 = 4`.
    -   `max_profit` becomes 4.
4.  **Day 4 (3)**:
    -   `3 > 1`. Profit `3 - 1 = 2`.
    -   `2 < 4`, no update.
5.  **Day 5 (6)**:
    -   `6 > 1`. Profit `6 - 1 = 5`.
    -   `max_profit` becomes 5.
6.  **Day 6 (4)**:
    -   `4 > 1`. Profit `3`.
    -   No update.

Final `max_profit` = 5.
