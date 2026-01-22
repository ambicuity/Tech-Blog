---
layout: page
title: "134. Gas Station"
permalink: /courses/leetcode/prob-134-gas-station/
---

# 134. Gas Station

## 1. The Question
There are `n` gas stations along a circular route, where the amount of gas at the `i`th station is `gas[i]`.

You have a car with an unlimited gas tank and it costs `cost[i]` of gas to travel from the `i`th station to its next `(i + 1)`th station. You begin the journey with an empty tank at one of the gas stations.

Given two integer arrays `gas` and `cost`, return the starting gas station's index if you can travel around the circuit once in the clockwise direction, otherwise return `-1`. If there exists a solution, it is **guaranteed** to be unique.

### Example 1
**Input**: `gas = [1,2,3,4,5]`, `cost = [3,4,5,1,2]`
**Output**: `3`
**Explanation**:
Start at station 3 (index 3) and fill up with 4 unit of gas. Your tank = 0 + 4 = 4.
Travel to station 4. Your tank = 4 - 1 + 5 = 8.
Travel to station 0. Your tank = 8 - 2 + 1 = 7.
Travel to station 1. Your tank = 7 - 3 + 2 = 6.
Travel to station 2. Your tank = 6 - 4 + 3 = 5.
Travel to station 3. The cost is 5. Your gas is just enough to travel back to station 3.
Therefore, return 3.

### Example 2
**Input**: `gas = [2,3,4]`, `cost = [3,4,3]`
**Output**: `-1`
**Explanation**:
You can't start at station 0 or 1, as there is not enough gas to travel to the next station.
Let's start at station 2 and fill up with 4 unit of gas. Your tank = 0 + 4 = 4.
Travel to station 0. Your tank = 4 - 3 + 2 = 3.
Travel to station 1. Your tank = 3 - 3 + 3 = 3.
You cannot travel back to station 2, as it requires 4 unit of gas but you only have 3.
Therefore, return -1.

---

## 2. Explanation
This problem has two key insights:
1.  **Global Feasibility**: If `sum(gas) < sum(cost)`, it is impossible to complete the circuit. Return -1 immediately.
2.  **Local Optimization (Greedy)**: If we start at station `A` and get stuck at station `B` (running out of fuel), then **no station between A and B** can be a valid starting point. Why? Because we arrived at any intermediate station with non-negative fuel and still failed. Starting there with 0 fuel would fail even earlier.
    -   So, if we fail at `i`, simply try starting at `i+1`.

### Approach
1.  Check `sum(gas) < sum(cost)`. If true, return -1.
2.  Iterate `i` from 0 to `n`:
    -   Add `gas[i] - cost[i]` to `current_tank`.
    -   If `current_tank < 0`:
        -   We failed. Reset `starting_station = i + 1`.
        -   Reset `current_tank = 0`.
3.  Return `starting_station`.

---

## 3. Pseudo Code
```text
If sum(gas) < sum(cost):
    Return -1

total_tank = 0
current_tank = 0
starting_station = 0

For i from 0 to n-1:
    total_tank += gas[i] - cost[i]
    current_tank += gas[i] - cost[i]
    
    If current_tank < 0:
        starting_station = i + 1
        current_tank = 0

Return starting_station
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def canCompleteCircuit(self, gas: list[int], cost: list[int]) -> int:
        # Insight 1: If total cost > total gas, impossible
        if sum(gas) < sum(cost):
            return -1
        
        current_tank = 0
        start = 0
        
        for i in range(len(gas)):
            current_tank += gas[i] - cost[i]
            
            # Insight 2: If we drop below zero, we can't start 
            # from 'start' or any node between 'start' and 'i'.
            # Reset start to i + 1.
            if current_tank < 0:
                start = i + 1
                current_tank = 0
                
        return start
```

---

## 5. Complexity
-   **Time**: $O(n)$. Single pass.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`gas = [1, 2, 3, 4, 5]`, `cost = [3, 4, 5, 1, 2]`
`sum(gas)=15`, `sum(cost)=15`. Possible.

1.  `i=0`. `diff = -2`. `curr = -2`.
    -   `curr < 0`: `start = 1`, `curr = 0`.
2.  `i=1`. `diff = -2`. `curr = -2`.
    -   `curr < 0`: `start = 2`, `curr = 0`.
3.  `i=2`. `diff = -2`. `curr = -2`.
    -   `curr < 0`: `start = 3`, `curr = 0`.
4.  `i=3`. `diff = +3`. `curr = 3`. (OK)
5.  `i=4`. `diff = +3`. `curr = 6`. (OK)

Loop end. Return `start = 3`.
