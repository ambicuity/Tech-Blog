---
layout: page
title: "DSA Ch.10: Elementary Structures"
permalink: /courses/dsa/ch10-elementary-data-structures/
---

# Chapter 10: Elementary Data Structures

> **Reference**: *Introduction to Algorithms* (CLRS), Chapter 10

In this chapter, we examine fundamental data structures used to represent dynamic sets.

## 10.1 Stacks and Queues
Dynamic sets where the element removed is prespecified.

### Stacks
- **LIFO** (Last-In, First-Out).
- Operations: `Push(S, x)`, `Pop(S)`.
- **Overflow**: Pushing to a full stack.
- **Underflow**: Popping from an empty stack.
- Complexity: $O(1)$.

### Queues
- **FIFO** (First-In, First-Out).
- Operations: `Enqueue(Q, x)`, `Dequeue(Q)`.
- Implemented using an array with `head` and `tail` pointers (wrapping around modulo $n$).
- Complexity: $O(1)$.

## 10.2 Linked Lists
A data structure where objects are arranged in a linear order. Unlike an array, the order is determined by a pointer in each object.

### Doubly Linked List
- Each element $x$ has:
    - `x.key`: The data.
    - `x.next`: Pointer to next element.
    - `x.prev`: Pointer to previous element.
- **Sentinel**: A dummy object `L.nil` that simplifies boundary conditions (turns the list into a circular list).
- Operations:
    - `Search(L, k)`: $\Theta(n)$.
    - `Insert(L, x)`: $O(1)$ (at head).
    - `Delete(L, x)`: $O(1)$ (if we have pointer to $x$).

## 10.3 Implementing Pointers and Objects
How do we implement linked list if the language doesn't support pointers? (e.g., Fortran).
- **Multiple Arrays**: Array for `key`, array for `next`, array for `prev`.
- **Single Array**: One large array where `key, next, prev` are at offsets $3i, 3i+1, 3i+2$.
