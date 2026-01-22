---
layout: page
title: "Arch Ch.1: Abstractions"
permalink: /courses/architecture/ch1-abstractions/
---

# Chapter 1: Computer Abstractions

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 1

Understanding the hardware/software interface is crucial for performance.

## 1.1 Seven Great Ideas in Architecture
1.  **Abstraction**: Hiding lower-level details (e.g., "Instruction Set").
2.  **Common Case Fast**: Optimize for the most frequent events (e.g., Caches).
3.  **Parallelism**: Doing things simultaneously.
4.  **Pipelining**: Overlapping execution stages (Assembly line).
5.  **Prediction**: Guessing the outcome of a branch before knowing it.
6.  **Hierarchy of Memories**: Register < Cache < RAM < Disk.
7.  **Dependability via Redundancy**.

## 1.2 Performance
What does it mean for a computer to be "faster"?
- **Response Time (Latency)**: Time between start and finish of a task.
- **Throughput (Bandwidth)**: Total amount of work done in a given time.

### The CPU Performance Equation
$$ \text{CPU Time} = \text{Instruction Count} \times \text{CPI} \times \text{Clock Cycle Time} $$
- **Instruction Count**: Determined by Program, ISA, and Compiler.
- **CPI (Cycles Per Instruction)**: Determined by CPU Hardware.
- **Clock Cycle Time**: Determined by Technology (Transistors).

To improve performance, we must reduce one of these three factors.

## 1.3 Power Wall
For decades, we increased clock speed (3 GHz -> 4 GHz).
But Power $\propto$ Capacity $\times$ Voltage$^2$ $\times$ Frequency.
We hit a thermal limit (The Power Wall). This forced the shift to **Multicore** processors instead of faster single cores.
