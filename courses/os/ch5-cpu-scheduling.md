---
layout: page
title: "OS Ch.5: CPU Scheduling"
permalink: /courses/os/ch5-cpu-scheduling/
---

# Chapter 5: CPU Scheduling

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 5

CPU scheduling is the basis of multiprogrammed operating systems. The OS must select which process in the ready queue gets the CPU next.

## 5.1 Basic Concepts
- **CPU-I/O Burst Cycle**: Processes alternate between CPU execution and I/O wait.
- **CPU Scheduler**: Selects a process from the short-term scheduler (Ready Queue).
- **Dispatcher**: The module that gives control of the CPU to the selected process (performs the context switch).

## 5.2 Scheduling Criteria
What makes a "good" scheduler?
- **CPU Utilization**: Keep CPU busy (40-90%).
- **Throughput**: Processes completed per time unit.
- **Turnaround Time**: Time from submission to completion.
- **Waiting Time**: Time spent waiting in the ready queue. (Best metric to optimize).
- **Response Time**: Time from submission to *first* response.

## 5.3 Scheduling Algorithms
1.  **FCFS (First-Come, First-Served)**:
    - FIFO Queue. Non-preemptive.
    - Problem: **Convoy Effect** (short processes stuck behind one big CPU-bound process).
2.  **SJF (Shortest Job First)**:
    - Assign CPU to process with smallest next CPU burst.
    - Probable optimal for average waiting time.
    - Problem: Hard to predict future burst length.
3.  **Priority Scheduling**:
    - Problem: **Starvation** (Low priority processes never execute).
    - Solution: **Aging** (Increase priority over time).
4.  **RR (Round Robin)**:
    - Time Quantum (q). FCFS but preemptive.
    - Fair, good response time.
    - Performance depends heavily on $q$. ($q$ large $\to$ FCFS. $q$ small $\to$ context switch overhead).
5.  **Multilevel Queue Scheduling**:
    - Different queues (Foreground/Interactive vs. Background/Batch).
    - Queueing between queues (Fixed priority or Time slice).

## 5.4 Multi-Processor Scheduling
- **Load Balancing**: Keep workload evenly distributed.
    - **Push migration**: Periodic task checks load and pushes.
    - **Pull migration**: Idle processor pulls waiting task.
- **Processor Affinity**: Process has populated cache on Core 1; try to keep it there.
