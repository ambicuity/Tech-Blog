---
layout: page
title: "DSA Ch.3: Growth of Functions"
permalink: /courses/dsa/ch3-growth-of-functions/
---

# Chapter 3: Growth of Functions

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 3

We drop lower-order terms and constants to focus on the rate of growth.

## 3.1 Asymptotic Notation
Definitions apply to functions $f(n), g(n)$ where domain is $\mathbb{N}$.

### $\Theta$-notation (Big-Theta)
Tight bound.
$$ \Theta(g(n)) = \{ f(n) : \exists c_1, c_2, n_0 \text{ such that } 0 \le c_1 g(n) \le f(n) \le c_2 g(n) \text{ for all } n \ge n_0 \} $$
*   "f(n) grows exactly as fast as g(n)".

### $O$-notation (Big-O)
Upper bound.
$$ O(g(n)) = \{ f(n) : \exists c, n_0 \text{ such that } 0 \le f(n) \le c g(n) \text{ for all } n \ge n_0 \} $$
*   "f(n) grows no faster than g(n)".
*   $f(n) = n^2 + 100 \implies f(n) \in O(n^2)$ and $f(n) \in O(n^3)$.

### $\Omega$-notation (Big-Omega)
Lower bound.
$$ \Omega(g(n)) = \{ f(n) : \exists c, n_0 \text{ such that } 0 \le c g(n) \le f(n) \text{ for all } n \ge n_0 \} $$
*   "f(n) grows at least as fast as g(n)".

---

## 3.2 Standard Notations
-   **Monotonicity**: $f(n) \le f(n+1)$.
-   **Floors/Ceilings**: $\lfloor x \rfloor, \lceil x \rceil$.
-   **Logarithms**: $\lg n = \log_2 n$, $\ln n = \log_e n$.
-   **Factorials**: $n! \approx \sqrt{2\pi n} (\frac{n}{e})^n$ (Stirling's approx). $\lg (n!) = \Theta(n \lg n)$.

## 3.3 Common Growth Rates
$$ 1 < \lg n < \sqrt{n} < n < n \lg n < n^2 < n^3 < 2^n < n! $$

---

## 3.4 Practical Complexity Calculation (Examples)

How do we calculate Time and Space complexity in practice?

### 1. Simple Loops ($O(N)$)
If a loop runs $N$ times and performs $O(1)$ constant work:
```python
# Time: O(N)
# Space: O(1)
for i in range(n):
    print(i)
```

### 2. Nested Loops ($O(N^2)$)
Inner loop runs $N$ times for *each* iteration of outer loop.
```python
# Time: O(N * N) = O(N^2)
for i in range(n):
    for j in range(n):
        print(i, j)
```

**Careful**: Dependent Loops.
```python
# Time: O(N^2)
# Inner loop runs i times: 1 + 2 + ... + N = N(N+1)/2
for i in range(n):
    for j in range(i):
        print(i, j)
```

### 3. Logarithmic Loops ($O(\log N)$)
If the variable is multiplied or divided each step.
```python
# Time: O(log N)
i = 1
while i < n:
    i = i * 2 
```
*   Step 1: 1
*   Step 2: 2
*   Step 3: 4
*   ...
*   Step k: $2^k$. Stop when $2^k > N \implies k > \lg N$.

### 4. Square Root ($O(\sqrt{N})$)
```python
# Time: O(sqrt(N))
i = 1
while (i * i) < n:
   i += 1
```

### 5. Consecutive Statements (Additivity)
We add complexities and drop lower terms.
```python
# Total Time: O(N) + O(N^2) = O(N^2)

for i in range(n):    # O(N)
    print(i)
    
for i in range(n):    # O(N^2)
    for j in range(n):
        print(i, j)
```

### 6. Recursion (Time & Space)
Complexity depends on depth of tree and branching factor.

**Example A: Factorial**
```python
def fact(n):
    if n == 0: return 1
    return n * fact(n-1)
```
*   **Time**: $T(n) = T(n-1) + O(1) \implies O(N)$.
*   **Space**: Stack depth is $N \implies O(N)$.

**Example B: Fibonacci (Naive)**
```python
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
```
*   **Time**: $T(n) \approx 2T(n-1) \implies O(2^N)$. (Exponential).
*   **Space**: Max stack depth is $N \implies O(N)$. (Not $2^N$, because memory is reused).

**Example C: Key Search in BST**
```python
def search(node, key):
    if not node: return
    if key < node.key: search(node.left, key)
    else: search(node.right, key)
```
*   **Time**: $O(H)$ where H is height.
    *   Balanced Tree: $O(\log N)$.
    *   Skewed Tree: $O(N)$.
*   **Space**: $O(H)$ (Stack frames).

### 7. Space Complexity: Auxiliary vs Total
*   **Auxiliary Space**: Extra space used (excluding input size).
*   **Total Space**: Input + Auxiliary.

**Example: Merging**
```python
def merge(arr1, arr2):
    res = [] # Auxiliary space O(N+M)
    ...
    return res
```
Here, Aux Space is $O(N)$.

**Example: In-Place Sort**
Insertion Sort uses $O(1)$ Aux space (just a few variables).
Merge Sort uses $O(N)$ Aux space (for the temporary arrays).
