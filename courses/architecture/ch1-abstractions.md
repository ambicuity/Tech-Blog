---
layout: page
title: "Arch Ch.1: Abstractions"
permalink: /courses/architecture/ch1-abstractions/
---

# Chapter 1: Computer Abstractions and Technology

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 1

## 1.1 Eight Great Ideas
1.  **Moore's Law**: Transistor density doubles every 18-24 months.
2.  **Abstraction**: Hiding lower-level details (ISA).
3.  **Make the Common Case Fast**: Optimization principle.
4.  **Parallelism**: Pipelining.
5.  **Pipelining**: Overlapping execution.
6.  **Prediction**: Branch prediction.
7.  **Hierarchy of Memories**: Caches.
8.  **Dependability via Redundancy**: RAID.

## 1.2 Performance
**Response Time (Latency)** vs **Throughput (Bandwidth)**.
$$ \text{Execution Time} = \frac{\text{Instructions}}{\text{Program}} \times \frac{\text{Cycles}}{\text{Instruction}} \times \frac{\text{Seconds}}{\text{Cycle}} $$
$$ Time = IC \times CPI \times Period $$
-   **MIPS Rating**: Millions of Instructions Per Second.

## 1.3 Power Wall
$P = C V^2 f$. We cannot increase frequency $f$ anymore because Power density creates too much heat. Shift to Multicore.
