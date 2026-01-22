---
layout: page
title: "DSA Ch.2: Getting Started"
permalink: /courses/dsa/ch2-getting-started/
---

# Chapter 2: Getting Started

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 2

We start with **Insertion Sort**, a simple algorithm that provides a framework for analyzing correctness and efficiency.

## 2.1 Insertion Sort
Efficient for small $n$. Works like sorting cards in hand.

```python
def insertion_sort(A):
    for j in range(1, len(A)):
        key = A[j]
        i = j - 1
        # Insert A[j] into sorted sequence A[0..j-1]
        while i >= 0 and A[i] > key:
            A[i + 1] = A[i]
            i = i - 1
        A[i + 1] = key
```

### Correctness: Loop Invariants
We use **Loop Invariants** to formally prove correctness, similar to Mathematical Induction.
**Invariant**: At the start of each iteration of the `for` loop, the subarray $A[0 \dots j-1]$ contains the elements originally in positions $0 \dots j-1$, but in sorted order.

1.  **Initialization**: Before first loop ($j=1$), subarray $A[0 \dots 0]$ contains 1 element. Trivially sorted. True.
2.  **Maintenance**: The body of the loop works by moving $A[j-1], A[j-2]$ etc one position right until proper spot for `key` is found. Thus $A[0 \dots j]$ becomes sorted. True.
3.  **Termination**: Loop ends when $j=n$. By invariant, $A[0 \dots n-1]$ is sorted. True.

---

## 2.2 Analyzing Algorithms
We use the **RAM Model** (Random Access Machine). Instructions (add, load, store) take constant time.

### Analysis of Insertion Sort
Let $c_i$ be cost of statement $i$.
$T(n) = c_1 n + c_2 (n-1) + \dots + c_5 \sum_{j=2}^n t_j$.
where $t_j$ is number of times the while loop tests.

-   **Best Case**: Sorted input. $t_j = 1$. $T(n) = \Theta(n)$. Linear.
-   **Worst Case**: Reverse sorted. $t_j = j$. $T(n) = \Theta(n^2)$. Quadratic.
-   **Average Case**: $\Theta(n^2)$.

---

## 2.3 Merge Sort (Divide & Conquer)
Recursive structure.
1.  **Divide**: Split into two halves.
2.  **Conquer**: Recursively sort halves.
3.  **Combine**: Merge two sorted lists.

```python
def merge(A, p, q, r):
    # Merges A[p..q] and A[q+1..r]
    # Complexity: Theta(n)
    ...
```

**Recurrence Relation**:
$$ T(n) = \begin{cases} \Theta(1) & \text{if } n=1 \\ 2T(n/2) + \Theta(n) & \text{if } n > 1 \end{cases} $$
Solution: $T(n) = \Theta(n \lg n)$.
*   Merge Sort beats Insertion Sort for $n > 30$.
