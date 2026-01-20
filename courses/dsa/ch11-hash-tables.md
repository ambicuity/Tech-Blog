---
layout: page
title: "DSA Ch.11: Hash Tables"
permalink: /courses/dsa/ch11-hash-tables/
---

# Chapter 11: Hash Tables

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 11

Many applications require a dynamic set that supports only `Insert`, `Search`, and `Delete`. A **Hash Table** is an effective data structure for this.

## 11.1 Direct-Address Tables
If the universe of keys $U$ is small (e.g., $0..99$), we can use an array $T[0..99]$.
- $O(1)$ operations.
- **Problem**: If $U$ is large ($2^{64}$), the table won't fit in memory.

## 11.2 Hash Tables
Use a **hash function** $h$ to compute the slot for key $k$: $h(k)$.
- This maps universe $U$ to small table $T[0..m-1]$.
- **Collision**: When two keys hash to the same slot ($h(k1) = h(k2)$).

## 11.3 Collision Resolution: Chaining
Put all elements that hash to the same slot in a **linked list**.
- **Analysis**:
    - Let $n$ be number of keys, $m$ be number of slots.
    - Load factor $\alpha = n/m$.
    - Simple Uniform Hashing: Any key is equally likely to hash into any of the $m$ slots.
    - Average search time: $\Theta(1 + \alpha)$.
    - If $m \propto n$, then $\Theta(1)$.

## 11.4 Collision Resolution: Open Addressing
Store all elements in the table itself. If collision, "probe" for next empty slot.
1.  **Linear Probing**: check $h(k), h(k)+1, h(k)+2...$
    - Problem: **Primary Clustering**. Long runs of occupied slots build up.
2.  **Quadratic Probing**: check $h(k) + c_1 i + c_2 i^2$.
3.  **Double Hashing**: $h(k, i) = (h_1(k) + i h_2(k)) \mod m$.
    - Best method for open addressing.

## 11.5 Universal Hashing
To prevent a malicious adversary from choosing keys that all hash to the same slot (DoS attack), select the hash function **randomly** from a carefully designed class of functions at runtime.
