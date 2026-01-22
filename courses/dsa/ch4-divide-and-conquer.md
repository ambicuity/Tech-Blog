---
layout: page
title: "DSA Ch.4: Divide-and-Conquer"
permalink: /courses/dsa/ch4-divide-and-conquer/
---

# Chapter 4: Divide-and-Conquer

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 4

## 4.1 The Maximum Subarray Problem
Find contiguous subarray with largest sum.

### Python Implementation (Kadane's Algorithm)
Dynamic Programming approach $O(n)$.

```python
def max_subarray(A):
    max_so_far = float('-inf')
    max_ending_here = 0
    start_index = 0
    end_index = 0
    temp_start = 0

    for i in range(len(A)):
        max_ending_here += A[i]
        
        if max_so_far < max_ending_here:
            max_so_far = max_ending_here
            start_index = temp_start
            end_index = i
        
        if max_ending_here < 0:
            max_ending_here = 0
            temp_start = i + 1
            
    return max_so_far, A[start_index : end_index+1]

# Example
arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
val, sub = max_subarray(arr)
print(f"Max Sum: {val}, Subarray: {sub}") 
# Output: Max Sum: 6, Subarray: [4, -1, 2, 1]
```

## 4.2 Strassen's Algorithm
Matrix Multiplication in $O(n^{2.81})$.
Standard: $C_{ij} = \sum A_{ik} B_{kj}$ ($O(n^3)$).
Strassen uses 7 multiplications of submatrices.

## 4.3 The Master Method
$T(n) = a T(n/b) + f(n)$.
1.  $f(n) < n^{\log_b a} \implies T(n) = \Theta(n^{\log_b a})$
2.  $f(n) = n^{\log_b a} \implies T(n) = \Theta(n^{\log_b a} \lg n)$
3.  $f(n) > n^{\log_b a} \implies T(n) = \Theta(f(n))$
