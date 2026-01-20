---
layout: page
title: "DSA Ch.1: Role of Algorithms"
permalink: /courses/dsa/ch1-foundations/
---

# Chapter 1: The Role of Algorithms in Computing

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 1

## 1.1 Algorithms as a Technology

An **algorithm** is any well-defined computational procedure that takes some value, or set of values, as **input** and produces some value, or set of values, as **output**.

An algorithm is thus a sequence of computational steps that transform the input into the output.

### Why "Technology"?
We often view hardware (CPUs, GPUs) as technology, but algorithms are just as critical.
- Faster hardware provides a linear speedup.
- Better algorithms can provide an exponential speedup.

**Example**:
Consider solving a problem of size $n=10^6$ (1 million items).
- **Supercomputer A** runs *Insertion Sort* ($O(n^2)$) at $10^8$ instructions/sec.
- **Laptop B** runs *Merge Sort* ($O(n \lg n)$) at $10^7$ instructions/sec.

**Time taken**:
- **Supercomputer A**: $\frac{(10^6)^2}{10^8} = 10,000$ seconds $\approx 2.7$ hours.
- **Laptop B**: $\frac{10^6 \lg 10^6}{10^7} \approx \frac{10^6 \times 20}{10^7} = 2$ seconds.

The profound difference shows that algorithms are a bounded resource, just like memory or CPU cycles. The choice of algorithm determines system scalability.

## 1.2 The Hard Questions

### What constitutes a "correct" algorithm?
An algorithm is said to be **correct** if, for every input instance, it halts with the correct output. An incorrect algorithm might not halt at all on some input instances, or it might halt with an incorrect answer.

### Key Data Structure Types
1.  **Linear**: Arrays, Linked Lists, Stacks, Queues.
2.  **Non-Linear**: Trees, Graphs.
3.  **Hashing**: Hash Tables, Bloom Filters.

## 1.3 NP-Complete Problems
There exists a class of problems called **NP-complete**.
- No efficient algorithm has ever been found for them.
- Nobody has proven that an efficient algorithm *cannot* exist.
- Solving one efficiently would allow solving *all* of them efficiently.

**Examples**: Traveling Salesman Problem (TSP), Clique Problem, Subset Sum.
**Strategy**: Since we cannot find the exact optimum efficiently, we often settle for **approximation algorithms**.
