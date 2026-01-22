---
layout: page
title: "13. Roman to Integer"
permalink: /courses/leetcode/prob-13-roman-to-integer/
---

# 13. Roman to Integer

## 1. The Question
Roman numerals are represented by seven different symbols: `I`, `V`, `X`, `L`, `C`, `D` and `M`.
-   `I`: 1
-   `V`: 5
-   `X`: 10
-   `L`: 50
-   `C`: 100
-   `D`: 500
-   `M`: 1000

For example, `2` is written as `II` in Roman numeral, just two ones added together. `12` is written as `XII`, which is simply `X + II`. The number `27` is written as `XXVII`, which is `XX + V + II`.

Roman numerals are usually written largest to smallest from left to right. However, the numeral for four is not `IIII`. Instead, the number four is written as `IV`. Because the one is before the five we subtract it making four. The same principle applies to the number nine, which is written as `IX`.

Given a roman numeral, convert it to an integer.

### Example 1
**Input**: `s = "III"`
**Output**: `3`

### Example 2
**Input**: `s = "LVIII"`
**Output**: `58`
**Explanation**: L = 50, V= 5, III = 3.

### Example 3
**Input**: `s = "MCMXCIV"`
**Output**: `1994`
**Explanation**: M = 1000, CM = 900, XC = 90 and IV = 4.

---

## 2. Explanation
Generally, we add the value of each symbol.
`X`: +10
`V`: +5
`I`: +1

The tricky part is subtraction: `IV` = 4.
The pattern: If a smaller value appears **before** a larger value, it is subtracted.
-   `I` (1) < `V` (5) -> `IV` is `5 - 1`.
-   `X` (10) < `C` (100) -> `XC` is `100 - 10`.

### Approach 1: Look Ahead
Iterate through the string. Compare current symbol `s[i]` with next symbol `s[i+1]`.
-   If `val(s[i]) < val(s[i+1])`: Subtract `val(s[i])`.
-   Else: Add `val(s[i])`.

### Approach 2: Reverse Iteration
If we iterate from right to left, we can track the "previous" value processed.
-   If `current_val < prev_val`: Subtract `current_val`.
-   Else: Add `current_val`.
(e.g., `IV`: We see `V` (5), total=5. prev=5. Then we see `I` (1). `1 < 5`, so subtract 1. total=4).

---

## 3. Pseudo Code (Left to Right)
```text
map = {'I': 1, 'V': 5, ...}
total = 0

For i from 0 to n-1:
    val = map[s[i]]
    
    # Check if there is a next symbol and if it's larger
    If i + 1 < n AND map[s[i+1]] > val:
        total -= val
    Else:
        total += val

Return total
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def romanToInt(self, s: str) -> int:
        roman_map = {
            'I': 1, 'V': 5, 'X': 10, 'L': 50,
            'C': 100, 'D': 500, 'M': 1000
        }
        
        total = 0
        n = len(s)
        
        for i in range(n):
            value = roman_map[s[i]]
            
            # If we are not at the last char AND next char is bigger
            if i + 1 < n and roman_map[s[i+1]] > value:
                total -= value
            else:
                total += value
                
        return total
```

---

## 5. Complexity
-   **Time**: $O(n)$.
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`s = "MCMXCIV"`

1.  `M` (1000). Next is `C` (100). `1000 > 100`. Add 1000. `tot=1000`.
2.  `C` (100). Next is `M` (1000). `100 < 1000`. Sub 100. `tot=900`.
3.  `M` (1000). Next is `X` (10). `1000 > 10`. Add 1000. `tot=1900`.
4.  `X` (10). Next is `C` (100). `10 < 100`. Sub 10. `tot=1890`.
5.  `C` (100). Next is `I` (1). `100 > 1`. Add 100. `tot=1990`.
6.  `X` - wait, missed skipping `XC`. Correct:
    -   (Rewind)
    -   `X` followed by `C` -> Subtract 10. `tot=1890`.
    -   `C` followed by `I` -> Add 100. `tot=1990`.
7.  `I` (1). Next is `V` (5). `1 < 5`. Sub 1. `tot=1989`.
8.  `V` (5). Last char. Add 5. `tot=1994`.
