---
layout: page
title: "DSA Ch.2: Getting Started"
permalink: /courses/dsa/ch2-getting-started/
---

# Chapter 2: Getting Started

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 2

This chapter introduces the framework for analyzing algorithms and design techniques using sorting as a primary example.

## 2.1 Insertion Sort
**Insertion Sort** is an efficient algorithm for sorting a small number of elements. It works the way many people sort a hand of playing cards.

### Algorithm
```python
def insertion_sort(A):
    for j in range(1, len(A)):
        key = A[j]
        i = j - 1
        # Insert A[j] into the sorted sequence A[0..j-1]
        while i >= 0 and A[i] > key:
            A[i + 1] = A[i]
            i = i - 1
        A[i + 1] = key
```

### Loop Invariant
To prove correctness, we use a **loop invariant**:
> At the start of each iteration of the for loop, the subarray $A[0..j-1]$ consists of the elements originally in $A[0..j-1]$, but in sorted order.

## 2.2 Analyzing Algorithms
Analysis involves predicting the resources (time and memory) computation requires.

- **Input Size ($n$)**: The number of items in the input (e.g., array size).
- **Running Time**: The number of primitive operations or steps executed.

### Analysis of Insertion Sort
- **Best Case**: Array is already sorted. The invariant loop (while) runs 0 times. Complexity: $\Theta(n)$.
- **Worst Case**: Array is reverse sorted. The while loop runs $j$ times. Complexity: $\Theta(n^2)$.
- **Average Case**: Often essentially as bad as the worst case. Complexity: $\Theta(n^2)$.

## 2.3 Designing Algorithms
There are many ways to design algorithms. Insertion sort uses an **incremental** approach. Another powerful technique is **Divide-and-Conquer**.

### Divide-and-Conquer
1.  **Divide**: Divide the problem into smaller subproblems.
2.  **Conquer**: Solve the subproblems recursively.
3.  **Combine**: Combine the solutions to create a solution for the original problem.

### Merge Sort
Merge Sort follows the divide-and-conquer paradigm.
1.  **Divide**: Divide the $n$-element sequence to be sorted into two subsequences of $n/2$ elements each.
2.  **Conquer**: Sort the two subsequences recursively using merge sort.
3.  **Combine**: Merge the two sorted subsequences to produce the sorted answer.

**Complexity**: $T(n) = 2T(n/2) + \Theta(n) \implies \Theta(n \lg n)$.
This is significantly faster than Insertion Sort for large $n$.
