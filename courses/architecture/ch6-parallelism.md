---
layout: page
title: "Arch Ch.6: Parallelism"
permalink: /courses/architecture/ch6-parallelism/
---

# Chapter 6: Parallel Processors from Client to Cloud

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 6

We cannot make single cores faster anymore (Power Wall). We must go parallel.

## 6.1 Difficulty of Parallel Programming
- **Partitioning**: Breaking job into parts.
- **Coordination**: Synchronization overhead.
- **Amdahl's Law**: Speedup is limited by the sequential part of the task.
    - If 10% of task must be serial, max speedup is 10x (even with 1000 cores).

## 6.2 Hardware Multithreading
Single core switches between threads very fast (when one stalls for cache miss).
- **Fine-grained**: Switch every cycle.
- **Coarse-grained**: Switch only on long stall (L3 miss).
- **SMT (Simultaneous Multithreading)**: Intel Hyper-Threading. Use functional units of ONE core to execute instructions from TWO threads simultaneously.

## 6.3 Multicore
Physical duplication of cores. Shared memory (L3 cache or RAM).
- **Cache Coherence**: If Core 1 changes X, Core 2 must see new X.
- **Snooping Protocols**: Caches watch the bus. If they see write to address they hold, they invalidate their copy.

## 6.4 GPUs (Graphics Processing Units)
SIMD (Single Instruction, Multiple Data).
- Execute same operation on thousands of data points (pixels/vectors).
- CUDA / OpenCL.
