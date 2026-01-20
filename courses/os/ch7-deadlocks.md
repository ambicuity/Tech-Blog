---
layout: page
title: "OS Ch.7: Deadlocks"
permalink: /courses/os/ch7-deadlocks/
---

# Chapter 7: Deadlocks

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 7

A **deadlock** is a situation where every process in a set is waiting for an event that can be caused only by another process in the set.
Example: P1 holds A, waits for B. P2 holds B, waits for A.

## 7.1 Necessary Conditions (Coffman Conditions)
Deadlock arises if and only if **all four** hold simultaneously:
1.  **Mutual Exclusion**: Resources are non-sharable.
2.  **Hold and Wait**: Process holding 1 resource is waiting for another.
3.  **No Preemption**: Resources cannot be forcibly taken.
4.  **Circular Wait**: P1 $\to$ P2 $\to$ ... $\to$ Pn $\to$ P1.

## 7.2 Methods for Handling Deadlocks
1.  **Prevention**: Ensure at least one of the 4 conditions cannot hold. (e.g., No Circular Wait: Order resources 1...N and require requests in increasing order).
2.  **Avoidance**: A priori information.
    - **Safe State**: A sequence exists to run everyone to completion.
    - **Banker's Algorithm**: Only grant request if it leaves system in Safe State.
3.  **Detection and Recovery**: Allow deadlock, detect it (Resource Allocation Graph), and recover (Terminate process or Preempt resources).
4.  **Ostrich Algorithm**: Ignore the problem. (Unix/Windows approach). Assume deadlocks are rare and cheaper to reboot than check.
