---
layout: page
title: "DSA Ch.11: Hash Tables"
permalink: /courses/dsa/ch11-hash-tables/
---

# Chapter 11: Hash Tables

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 11

Dictionary operations (Insert, Search, Delete) in $O(1)$ average time.

## 11.1 Direct Address Table
If universe $U$ is small, just use an array. Fast but takes $|U|$ space.

## 11.2 Hash Tables
Use function $h(k)$ to map $U \to 0 \dots m-1$.
**Collisions**: When $h(k_1) = h(k_2)$.

### Chaining
Store linked list at each bucket.
-   Load factor $\alpha = n/m$.
-   Expected search time $\Theta(1 + \alpha)$.

### Open Addressing
All elements stored in table. If collision, **Probe** for next slot.
1.  **Linear Probing**: $h(k, i) = (h'(k) + i) \pmod m$. (Primary Clustering problem).
2.  **Quadratic Probing**: $h(k, i) = (h'(k) + c_1 i + c_2 i^2) \pmod m$.
3.  **Double Hashing**: $h(k, i) = (h_1(k) + i h_2(k)) \pmod m$. Best distribution.

## 11.3 Universal Hashing
A malicious adversary can choose keys that map to same slot (DOS attack).
Solution: Choose hash function **randomly** from a carefully designed family of functions.
$$ P(h(k_1) = h(k_2)) \le 1/m $$
Example: $h_{a,b}(k) = ((ak+b) \pmod p) \pmod m$.
