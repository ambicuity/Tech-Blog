---
layout: page
title: "OS Ch.3: Processes"
permalink: /courses/os/ch3-processes/
---

# Chapter 3: Processes

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 3

A **process** is a program in execution. It is the unit of work in a modern time-sharing system.

## 3.1 Process Concept
A process is more than the program code (**Text Section**). It also includes:
- **Program Counter**: Current activity.
- **Stack**: Temporary data (function parameters, return addresses, local variables).
- **Data Section**: Global variables.
- **Heap**: Memory dynamically allocated during run time.

**States**:
1.  **New**: Being created.
2.  **Running**: Instructions are being executed.
3.  **Waiting**: Waiting for an event (I/O).
4.  **Ready**: Waiting to be assigned to a processor.
5.  **Terminated**: Finished execution.

## 3.2 Process Control Block (PCB)
Each process is represented in the OS by a PCB (Task Control Block).
- Process State
- Program Counter
- CPU Registers
- CPU-scheduling information (Priority)
- Memory-management information (Page tables)
- I/O status information (Open files)

## 3.3 Process Scheduling
The objective of multiprogramming is to have some process running at all times to maximize CPU utilization.
- **Job Queue**: All processes.
- **Ready Queue**: Processes in main memory, ready to run.
- **Device Queue**: Processes waiting for an I/O device.

**Context Switch**:
When switching the CPU to another process, the system must **save** the state of the old process and **load** the saved state for the new process. This is pure overhead.

## 3.4 Operations on Processes
### Process Creation via `fork()` (UNIX)
- `fork()` system call creates a new process (child) which is an exact copy of the parent.
- Returns `0` to the child, and `pid` of child to the parent.
- Usually followed by `exec()` to replace the child's memory space with a new program.

### Process Termination
- `exit()`: Process asks OS to delete it.
- `wait()`: Parent waits for child to terminate.
- **Zombie Process**: A process that has terminated, but whose parent has not yet called `wait()`.
- **Orphan Process**: Parent terminated without invoking `wait()`.
