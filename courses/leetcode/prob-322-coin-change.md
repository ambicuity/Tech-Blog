---
layout: page
title: "322. Coin Change"
permalink: /courses/leetcode/prob-322-coin-change/
---

# 322. Coin Change

## 1. The Question
You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money.

Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return `-1`.

You may assume that you have an infinite number of each kind of coin.

### Example 1
**Input**: `coins = [1,2,5], amount = 11`
**Output**: `3`
**Explanation**: `11 = 5 + 5 + 1`.

### Example 2
**Input**: `coins = [2], amount = 3`
**Output**: `-1`

---

## 2. Explanation
This is the **Unbounded Knapsack** problem (minimization variant).
DP State: `dp[i]` = min coins to make amount `i`.
Transition: For each coin `c` in `coins`:
`dp[i] = min(dp[i], dp[i - c] + 1)` (if `i >= c`).

Init: `dp[0] = 0`. All other `dp[i] = infinity`.
Final result: `dp[amount]`. If `infinity`, return -1.

-   **Time**: $O(A \cdot N)$, where A is amount, N is number of coins.
-   **Space**: $O(A)$.

---

## 3. Pseudo Code
```text
dp = [inf] * (amount + 1)
dp[0] = 0

for a in 1..amount:
    for c in coins:
        if a - c >= 0:
            dp[a] = min(dp[a], 1 + dp[a-c])

return dp[amount] if dp[amount] != inf else -1
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def coinChange(self, coins: list[int], amount: int) -> int:
        # Initialize dp array with amount + 1 (impossible value)
        dp = [amount + 1] * (amount + 1)
        dp[0] = 0
        
        for a in range(1, amount + 1):
            for c in coins:
                if a - c >= 0:
                    dp[a] = min(dp[a], 1 + dp[a - c])
                    
        return dp[amount] if dp[amount] <= amount else -1
```

---

## 5. Complexity
-   **Time**: $O(S \cdot n)$. S is amount, n is coin count.
-   **Space**: $O(S)$.

## 6. Example Walkthrough
`coins=[1,2,5]`, `amount=6`.
1.  `dp[0]=0`.
2.  `dp[1]`. `1`: `1+dp[0]=1`. Min 1.
3.  `dp[2]`. `1`: `1+dp[1]=2`. `2`: `1+dp[0]=1`. Min 1.
4.  `dp[3]`. `1`: `1+dp[2]=2`. `2`: `1+dp[1]=2`. Min 2.
5.  `dp[4]`. `1`: `2+1=3`. `2`: `2+1=2`. Min 2.
6.  `dp[5]`. `1`: `2+1=3`. `2`: `2+1=3`. `5`: `1+dp[0]=1`. Min 1.
7.  `dp[6]`. `1`: `1+1=2`. `2`: `1+2=3`. `5`: `1+1=2`. Min 2.
Result 2 (`5+1` or `1+5`). Wait... `5+1`. `3+3` if 3 existed.
Wait `dp[6]` from `5` is `1+dp[1]=2`. Correct. `5+1`.
Also `dp[4]+2` (2+1=3). Correct.
