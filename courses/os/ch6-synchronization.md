---
layout: page
title: "OS Ch.6: Synchronization"
permalink: /courses/os/ch6-synchronization/
---

# Chapter 6: Process Synchronization

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 6

Processes executing concurrently may be interrupted at any time. If they share data, this can lead to **Race Conditions** where the outcome depends on the order of execution.

## 6.1 The Critical-Section Problem
n processes compete to use shared data. Each has a code segment called a **Critical Section**.
**Requirements**:
1.  **Mutual Exclusion**: Only one process in CS at a time.
2.  **Progress**: If no one is in CS, we must decide who enters next (cannot be blocked by a process outside CS).
3.  **Bounded Waiting**: A limit on how many times others can enter CS before a requesting process is granted access.

## 6.2 Hardware Support
- **Memory Barriers**: Instructions that force order of memory access.
- **Hardware Instructions**: Atomic operations like `TestAndSet` or `CompareAndSwap` (CAS).

## 6.3 Mutex Locks
Software tool available to API designers.
- `acquire()`: Wait until available.
- `release()`: Signal completion.
- Uses **Busy Waiting** (Spinlock) in simple implementations.

## 6.4 Semaphores
A stronger synchronization tool. An integer variable accessed only via `wait()` (P) and `signal()` (V).
- **Binary Semaphore**: 0 or 1. Same as Mutex.
- **Counting Semaphore**: Manage a resource pool (e.g., 5 printers).
- **Implementation**: Instead of busy waiting, a process blocks itself (moves to Waiting Queue) if semaphore is $\le 0$.

## 6.5 Monitors
A high-level language construct (e.g., `synchronized` in Java).
- A class/module where only one thread can be active at a time.
- **Condition Variables**: `wait()` and `signal()` within the monitor to coordinate specific states (e.g., Buffer Not Empty).
