---
layout: page
title: "68. Text Justification"
permalink: /courses/leetcode/prob-68-text-justification/
---

# 68. Text Justification

## 1. The Question
Given an array of strings `words` and a width `maxWidth`, format the text such that each line has exactly `maxWidth` characters and is fully (left and right) justified.

You should pack your words in a greedy approach; that is, pack as many words as you can in each line. Pad extra spaces `' '` when necessary so that each line has exactly `maxWidth` characters.

Extra spaces between words should be distributed as evenly as possible. If the number of spaces on a line does not divide evenly between words, the empty slots on the left will be assigned more spaces than the slots on the right.

For the last line of text, it should be left-justified, and no extra space is inserted between words.

### Example 1
**Input**: `words = ["This", "is", "an", "example", "of", "text", "justification."], maxWidth = 16`
**Output**:
```
[
   "This    is    an",
   "example  of text",
   "justification.  "
]
```

### Example 2
**Input**: `words = ["What","must","be","acknowledgment","shall","be"], maxWidth = 16`
**Output**:
```
[
  "What   must   be",
  "acknowledgment  ",
  "shall be        "
]
```

---

## 2. Explanation
This is a simulation problem. We need to build lines word by word.

### Rules of Thumb:
1.  **Line Construction**: Keep adding words to `current_line` until `len(words) + len(spaces) + len(next_word)` exceeds `maxWidth`.
2.  **Regular Line Justification**:
    -   Spaces needed = `maxWidth - sum(len(words in line))`.
    -   Slots for spaces = `len(words in line) - 1`.
    -   If one word: Just left align.
    -   Else:
        -   `base_space = spaces // slots`
        -   `extra_space = spaces % slots`
        -   The first `extra_space` slots get `base_space + 1` spaces. The rest get `base_space`.
3.  **Last Line Justification**:
    -   Left justify: Join words with **single space**.
    -   Pad remaining space at the end to match `maxWidth`.

---

## 3. Pseudo Code
```text
lines = []
current_line = []
curr_len = 0

For word in words:
    # Check if adding word exceeds maxWidth
    # We need len(current_line) spaces for separation
    if curr_len + len(word) + len(current_line) > maxWidth:
        # Justify current_line and add to result
        lines.append(justify(current_line))
        
        # Reset
        current_line = [word]
        curr_len = len(word)
    else:
        current_line.append(word)
        curr_len += len(word)

# Handle Leftover (Last Line)
lines.append(left_justify(current_line))
Return lines
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def fullJustify(self, words: list[str], maxWidth: int) -> list[str]:
        res = []
        current_line = []
        current_len = 0
        
        for word in words:
            # Check if adding this word + necessary 1 space per existing word overflows
            # len(current_line) is the number of spaces if we just use single spaces
            if current_len + len(word) + len(current_line) > maxWidth:
                
                # --- JUSTIFY THE LINE WE JUST FINISHED ---
                
                # Spaces to distribute
                total_spaces = maxWidth - current_len
                
                # Gaps between words
                gaps = len(current_line) - 1
                
                if gaps == 0:
                    # Case: Single word in line
                    res.append(current_line[0] + ' ' * total_spaces)
                else:
                    # Regular case: Distribute spaces
                    space_per_gap = total_spaces // gaps
                    extra_spaces = total_spaces % gaps
                    
                    line_str = ""
                    for i in range(gaps):
                        # Construct line: Word + Spaces
                        line_str += current_line[i]
                        
                        # Add base spaces
                        line_str += ' ' * space_per_gap
                        
                        # Add extra space if this gap is one of the "lucky" left ones
                        if i < extra_spaces:
                            line_str += ' '
                            
                    # Add last word (no spaces after it)
                    line_str += current_line[-1]
                    res.append(line_str)
                
                # --- RESET FOR NEW LINE ---
                current_line = []
                current_len = 0
            
            current_line.append(word)
            current_len += len(word)
            
        # --- HANDLE LAST LINE ---
        # "For the last line of text, it should be left-justified"
        last_line = ' '.join(current_line)
        remaining_spaces = maxWidth - len(last_line)
        res.append(last_line + ' ' * remaining_spaces)
        
        return res
```

---

## 5. Complexity
-   **Time**: $O(n)$ where `n` is total characters in `words`. We iterate through words and build strings linearly.
-   **Space**: $O(maxWidth)$ for building lines. $O(n)$ for result.

## 6. Example Walkthrough
`words = ["This", "is", "an", "example"]`, `width = 16`

1.  Add "This", "is", "an". `len = 4+2+2 = 8`. Gaps needed = 2. `8 + 2 <= 16`.
2.  Next "example" (7). `8 + 7 + 3 (gaps) = 18 > 16`. **Overflow**.
3.  **Justify Line 1**: `["This", "is", "an"]`.
    -   `chars = 8`. `total_spaces = 16 - 8 = 8`.
    -   `gaps = 2`.
    -   `space_per_gap = 8 // 2 = 4`.
    -   `extra = 0`.
    -   Result: `"This" + "    " + "is" + "    " + "an"` (Length 16).
4.  **Reset**: `current_line = ["example"]`. `len=7`.
5.  End loop.
6.  **Last Line**: `Justify(["example"])`.
    -   Join with ' ': `"example"`.
    -   Pad right: `"example         "` (9 spaces).
