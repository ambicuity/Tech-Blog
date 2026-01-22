---
layout: page
title: "6. Zigzag Conversion"
permalink: /courses/leetcode/prob-6-zigzag-conversion/
---

# 6. Zigzag Conversion

## 1. The Question
The string `"PAYPALISHIRING"` is written in a zigzag pattern on a given number of rows like this: (you may want to display this pattern in a fixed font for better legibility)

```
P   A   H   N
A P L S I I G
Y   I   R
```
And then read line by line: `"PAHNAPLSIIGYIR"`

Write the code that will take a string and make this conversion given a number of rows.

### Example 1
**Input**: `s = "PAYPALISHIRING", numRows = 3`
**Output**: `"PAHNAPLSIIGYIR"`

### Example 2
**Input**: `s = "PAYPALISHIRING", numRows = 4`
**Output**: `"PINALSIGYAHRPI"`
**Explanation**:
```
P     I    N
A   L S  I G
Y A   H R
P     I
```

---

## 2. Explanation
We need to place characters into rows.
The pattern repeats:
-   Go **down** from Row 0 to Row `numRows-1`.
-   Go **up** from Row `numRows-1` to Row 0.
-   Repeat.

We can simulate this by maintaining a list of strings (one for each row). We iterate through the input string `s` and append each character to the current row. Then we update the current row (up or down).
-   If current row == 0, direction -> Down (+1).
-   If current row == numRows - 1, direction -> Up (-1).

### Approach: Simulation
-   Create `rows = [""] * numRows`
-   `curRow = 0`
-   `goingDown = False`
-   Loop char in string:
    -   `rows[curRow] += char`
    -   If `curRow == 0` or `curRow == numRows - 1`, toggle `goingDown`.
    -   `curRow += 1` if `goingDown` else `-1`.
-   Join all rows.

-   **Time**: $O(n)$ where $n$ is length of string.
-   **Space**: $O(n)$ to store the result.

---

## 3. Pseudo Code
```text
If numRows == 1: return s

rows = list of empty strings of size numRows
curr_row = 0
step = 0

For c in s:
    rows[curr_row].append(c)
    
    If curr_row == 0:
        step = 1
    Else If curr_row == numRows - 1:
        step = -1
        
    curr_row += step

Return join(rows)
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def convert(self, s: str, numRows: int) -> str:
        if numRows == 1 or numRows >= len(s):
            return s
            
        # Create a list of strings for each row
        rows = [''] * numRows
        
        curr_row = 0
        step = 1
        
        for char in s:
            rows[curr_row] += char
            
            # Change direction if we hit top or bottom
            if curr_row == 0:
                step = 1
            elif curr_row == numRows - 1:
                step = -1
                
            curr_row += step
            
        return ''.join(rows)
```

---

## 5. Complexity
-   **Time**: $O(n)$. We visit every character once.
-   **Space**: $O(n)$. We store the entire string in rows.

## 6. Example Walkthrough
`s = "PAYPAL"`, `numRows = 3`

1.  `P`: `rows[0] = "P"`. `curr=0` -> `step=1`. `curr` becomes 1.
2.  `A`: `rows[1] = "A"`. `curr` becomes 2.
3.  `Y`: `rows[2] = "Y"`. `curr=2` -> `step=-1`. `curr` becomes 1.
4.  `P`: `rows[1] = "AP"`. `curr` becomes 0.
5.  `A`: `rows[0] = "PA"`. `curr=0` -> `step=1`. `curr` becomes 1.
6.  `L`: `rows[1] = "APL"`. `curr` becomes 2.

Final Rows:
0: "PA"
1: "APL"
2: "Y"
Join: "PAAPLY".
