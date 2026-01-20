---
layout: page
title: "DSA Ch.7: Quicksort"
permalink: /courses/dsa/ch7-quicksort/
---

# Chapter 7: Quicksort

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 7

Quicksort is typically the fastest sorting algorithm in practice.
- **Worst-case**: $\Theta(n^2)$ (Rare with randomization).
- **Average-case**: $\Theta(n \lg n)$.
- **In-place**: Yes.

## 7.1 Description
Divide-and-conquer:
1.  **Divide**: Partition array $A[p..r]$ into two subarrays $A[p..q-1]$ and $A[q+1..r]$ such that every element in the left is $\le A[q]$ and every element in the right is $\ge A[q]$.
2.  **Conquer**: Sort the two subarrays recursively.
3.  **Combine**: Nothing to do (sorted in place).

### Partitioning
The key to Quicksort is the `Partition` procedure.
```python
def partition(A, p, r):
    x = A[r] # Pivot
    i = p - 1
    for j in range(p, r):
        if A[j] <= x:
            i = i + 1
            exchange A[i] with A[j]
    exchange A[i+1] with A[r]
    return i + 1
```

## 7.2 Performance
- **Worst Case**: Input is already sorted or reverse sorted. Partition always produces one subproblem of size $n-1$ and one of 0. Result: $T(n) = T(n-1) + \Theta(n) \to \Theta(n^2)$.
- **Best Case**: Partition splits in middle. $T(n) = 2T(n/2) + \Theta(n) \to \Theta(n \lg n)$.

## 7.3 Randomized Quicksort
To prevent worst-case behavior on sorted inputs, we pick a **random** element as the pivot (swap $A[r]$ with random $A[k]$).
- This makes the expected running time $\Theta(n \lg n)$ for *any* input.
