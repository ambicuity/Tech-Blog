---
layout: page
title: "DBMS Ch.11: Hash Indexing"
permalink: /courses/dbms/ch11-hash-indexing/
---

# Chapter 11: Hash-Based Indexing

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 11

Best for equality searches (`WHERE id = 5`), but useless for range searches (`WHERE age > 18`).

## 11.1 Static Hashing
- **Hash Function** $h(k)$ maps key to bucket number $0 \dots N-1$.
- **Collisions**: If bucket is full, use overflow chains (linked list).
- Problem: If file grows, chains get long, performance degrades to $O(N)$.

## 11.2 Extendible Hashing
Dynamic hashing technique.
- Use a **Directory** of pointers to buckets.
- Directory size is $2^d$ (where $d$ is global depth).
- When bucket overflows, split it and double the directory size (if needed).
- **Cost**: One extra I/O for directory lookup, but no overflow chains.

## 11.3 Linear Hashing
- Avoids directories.
- Split buckets in linear order (0, then 1, then 2...) regardless of which one overflowed.
- Uses "Next" pointer to track splits.
