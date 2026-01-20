---
layout: page
title: "OS Ch.4: Threads"
permalink: /courses/os/ch4-threads-concurrency/
---

# Chapter 4: Threads & Concurrency

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 4

A **thread** is a basic unit of CPU utilization. It comprises a thread ID, a program counter, a register set, and a stack.

## 4.1 Overview
A traditional (heavyweight) process has a single thread of control. If a process has multiple threads of control, it can perform more than one task at a time.

**Shared Resources** (within a process):
- Code section
- Data section
- OS resources (open files, signals)

**Private Resources** (per thread):
- Registers
- Stack
- Program Counter

**Benefits**:
1.  **Responsiveness**: Web browser can render and download simultaneously.
2.  **Resource Sharing**: Threads share memory (easier than Shared Memory/Message Passing between processes).
3.  **Economy**: Creating a thread is cheaper than creating a process. Context switching threads is faster.
4.  **Scalability**: Logic works well on Multicore architectures.

## 4.2 Multicore Programming
- **Parallelism**: System runs multiple tasks literally simultaneously (multiple cores).
    - **Data Parallelism**: Same data, split across cores.
    - **Task Parallelism**: Distinct threads doing different tasks.
- **Concurrency**: System supports more than one task making progress (time-slicing on single core).

## 4.3 Multithreading Models
User threads (library level) must be mapped to Kernel threads.

1.  **Many-to-One**: Many user threads mapped to one kernel thread.
    - Blocking call blocks all threads.
    - No true parallelism (only one kernel thread).
    - Example: Green Threads (Java 1.1).

2.  **One-to-One**: Each user thread maps to a kernel thread.
    - True parallelism.
    - Overhead of creating kernel threads.
    - Example: Linux, Windows.

3.  **Many-to-Many**: M user threads multiplexed to N kernel threads ($M \ge N$).
    - Example: Go Routines (Go Scheduler).

## 4.4 Thread Libraries
- **Pthreads**: POSIX standard (IEEE 1003.1c) API for thread creation/synchronization. (Specification, not implementation).
- **Java Threads**: Managed by JVM.
