---
layout: page
title: "125. Valid Palindrome"
permalink: /courses/leetcode/prob-125-valid-palindrome/
---

# 125. Valid Palindrome

## 1. The Question
A phrase is a **palindrome** if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.

Given a string `s`, return `true` if it is a palindrome, or `false` otherwise.

### Example 1
**Input**: `s = "A man, a plan, a canal: Panama"`
**Output**: `true`
**Explanation**: "amanaplanacanalpanama" is a palindrome.

### Example 2
**Input**: `s = "race a car"`
**Output**: `false`
**Explanation**: "raceacar" is not a palindrome.

### Example 3
**Input**: `s = " "`
**Output**: `true`
**Explanation**: s is an empty string "" after removing non-alphanumeric characters.
Since an empty string reads the same forward and backward, it is a palindrome.

---

## 2. Explanation
We need to check if the string matches its reverse, ignoring case and special symbols.

### Approach 1: Filter and Reverse
1.  Create a new string containing only lowercase alphanumeric chars.
2.  Check if `new_string == new_string[::-1]`.
-   **Time**: $O(n)$
-   **Space**: $O(n)$ (for new string)

### Approach 2: Two Pointers (Optimal)
Use `left` pointer at start, `right` pointer at end.
1.  Move `left` forward until it hits an alphanumeric char.
2.  Move `right` backward until it hits an alphanumeric char.
3.  Compare characters (lowercased). If mismatch, return `False`.
4.  Move both inward.
-   **Time**: $O(n)$
-   **Space**: $O(1)$

---

## 3. Pseudo Code (Two Pointers)
```text
left = 0, right = length(s) - 1

While left < right:
    If s[left] is not alphanumeric:
        left++
        Continue
    If s[right] is not alphanumeric:
        right--
        Continue
    
    If lower(s[left]) != lower(s[right]):
        Return False
        
    left++, right--

Return True
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def isPalindrome(self, s: str) -> bool:
        left, right = 0, len(s) - 1
        
        while left < right:
            # Move left pointer forward until we find an alphanumeric char
            while left < right and not s[left].isalnum():
                left += 1
                
            # Move right pointer backward similarly
            while left < right and not s[right].isalnum():
                right -= 1
                
            # Compare characters
            if s[left].lower() != s[right].lower():
                return False
                
            # Move pointers inward
            left += 1
            right -= 1
            
        return True
```

---

## 5. Complexity
-   **Time**: $O(n)$. We traverse the string exactly once.
-   **Space**: $O(1)$. No extra strings created.

## 6. Example Walkthrough
`s = "A man..."`

1.  `L` at 'A', `R` at 'a'. Match.
2.  `L` skips ' ', moves to 'm'. `R` at 'm'. Match.
3.  `L` at 'a', `R` at 'a'. Match.
4.  `L` at 'n', `R` at 'n'. Match.
5.  `L` skips ',', ' ', moves to 'a'. `R` skips ' ', ':', 'l', 'a', 'n', 'a', 'c', 'a', moves to... wait.
    (Detailed scan):
    `L` -> 'a' (index 3). `R` -> 'a' (panam`a`).
    ...
    Eventually `L` and `R` meet in middle.
