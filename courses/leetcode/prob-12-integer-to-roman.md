---
layout: page
title: "12. Integer to Roman"
permalink: /courses/leetcode/prob-12-integer-to-roman/
---

# 12. Integer to Roman

## 1. The Question
Seven different symbols represent Roman numerals with the following values:
`I`: 1, `V`: 5, `X`: 10, `L`: 50, `C`: 100, `D`: 500, `M`: 1000

Roman numerals are formed by appending the conversions of decimal place values from highest to lowest. Converting a decimal place value into a Roman numeral has the following rules:
-   If the value does not start with 4 or 9, select the symbol of the maximal value that can be subtracted from the input, append that symbol to the result, subtract its value, and convert the remainder to a Roman numeral.
-   If the value starts with 4 or 9 use the subtractive form representing one symbol subtracted from the following symbol, for example 4 is 1 (`I`) less than 5 (`V`): `IV` and 9 is 1 (`I`) less than 10 (`X`): `IX`. Only the following subtractive forms are used: 4 (`IV`), 9 (`IX`), 40 (`XL`), 90 (`XC`), 400 (`CD`) and 900 (`CM`).
-   Only powers of 10 (`I`, `X`, `C`, `M`) can be appended consecutively at most 3 times to represent multiples of 10. You cannot append 5 (`V`), 50 (`L`), or 500 (`D`) multiple times. If you need to append a symbol 4 times use the subtractive form.

Given an integer, convert it to a Roman numeral.

### Example 1
**Input**: `num = 3749`
**Output**: `"MMMDCCXLIX"`
**Explanation**:
3000 = MMM
 700 = DCC
  40 = XL
   9 = IX
--> MMMDCCXLIX

### Example 2
**Input**: `num = 58`
**Output**: `"LVIII"`

---

## 2. Explanation
This is the reverse of "Roman to Integer".
Since the rules about 4 and 9 are specific, we can treat them as their own symbols.
List of **Values vs Symbols** (Sorted Descending):
-   1000: M
-   900: CM
-   500: D
-   400: CD
-   100: C
-   90: XC
-   50: L
-   40: XL
-   10: X
-   9: IX
-   5: V
-   4: IV
-   1: I

We iterate through this list. If `num >= value`, we subtract the value from `num` and append the symbol to the result. We repeat this until `num < value`, then move to the next smaller value.

### Approach: Greedy (With Subtractive Pairs)
-   Store `(value, symbol)` tuples in descending order.
-   While `num > 0`:
    -   Find largest `value <= num`.
    -   Subtract `value` from `num`.
    -   Append `symbol` to result.
    -   (Or effectively: `count = num // value`, append `symbol * count`, `num %= value`).

-   **Time**: $O(1)$. Since maximum input is 3999, the loops are fixed/constant.
-   **Space**: $O(1)$.

---

## 3. Pseudo Code
```text
values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
symbols = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
res = ""

For i from 0 to 12:
    While num >= values[i]:
        num -= values[i]
        res += symbols[i]

Return res
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def intToRoman(self, num: int) -> str:
        # Mapping of integer values to Roman symbols
        # Must be in descending order to work greedily
        val_map = [
            (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
            (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
            (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
        ]
        
        result = []
        
        for value, symbol in val_map:
            # If num is 0, we are done
            if num == 0:
                break
                
            # How many times does this value fit?
            # e.g., if num=20 and value=10, count=2
            count, num = divmod(num, value)
            
            # Append symbol 'count' times
            result.append(symbol * count)
            
        return "".join(result)
```

---

## 5. Complexity
-   **Time**: $O(1)$. Although there are loops, the number of iterations is bounded because the input `num` is bounded (typically $< 4000$) and the number of Roman symbols is small (13).
-   **Space**: $O(1)$.

## 6. Example Walkthrough
`num = 1994`

1.  `1000 (M)`: `1994 // 1000 = 1`. `res="M"`. `rem=994`.
2.  `900 (CM)`: `994 // 900 = 1`. `res="MCM"`. `rem=94`.
3.  `500 (D)`: `94 < 500`. Skip.
4.  `...`
5.  `90 (XC)`: `94 // 90 = 1`. `res="MCMXC"`. `rem=4`.
6.  `...`
7.  `4 (IV)`: `4 // 4 = 1`. `res="MCMXCIV"`. `rem=0`.
8.  Stop.
