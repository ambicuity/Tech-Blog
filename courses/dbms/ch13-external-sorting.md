---
layout: page
title: "DBMS Ch.13: External Sorting"
permalink: /courses/dbms/ch13-external-sorting/
---

# Chapter 13: External Sorting

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 13

What if we need to sort 10 GB of data but only have 1 GB of RAM? Standard QuickSort fails (swapping pages causes thrashing).

## 13.1 Two-Way Merge Sort
Idea: Divide and Conquer on disk.
1.  **Read** partial data, sort in memory, **Write** run.
2.  **Merge** runs together.

## 13.2 General External Merge Sort
Suppose we have $B$ buffer pages in RAM.
- **Pass 0 (Sorting)**: Read $B$ pages, sort them into a run, write out.
    - Produces $N/B$ runs of size $B$.
- **Pass 1, 2, ... (Merging)**: Merge $B-1$ runs at a time.
    - Number of passes = $\lceil \log_{B-1} (N/B) \rceil$.

## 13.3 Optimizations
- **Double Buffering**: Prefetch next block while CPU processes current block.
- **Blocked I/O**: Read larger chunks to minimize seek time.
- **Tournament Sort**: Using a heap to produce initial runs larger than $B$.
