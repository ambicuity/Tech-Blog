---
layout: page
title: "OS Ch.1: Introduction"
permalink: /courses/os/ch1-introduction/
---

# Chapter 1: Introduction to Operating Systems

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 1

An **Operating System (OS)** is a program that acts as an intermediary between a user of a computer and the computer hardware.

## 1.1 What does an OS do?
- **User View**: Ease of use, performance. (e.g., PC, Mobile).
- **System View**: Resource allocator. The OS acts as the **manager** of resources:
    - CPU time
    - Memory space
    - File-storage space
    - I/O devices

**The Kernel**: The one program running at all times on the computer. Everything else is either a system program (ships with OS) or an application program.

## 1.2 Computer-System Organization

### Interrupts
An **interrupt** is a signal to the CPU that an event has occurred.
1.  Hardware triggers an interrupt by sending a signal via the system bus.
2.  CPU stops what it is doing and transfers execution to a fixed location (the **Interrupt Vector**).
3.  The **Interrupt Service Routine (ISR)** executes.
4.  CPU resumes the interrupted computation.

### Storage Structure
- **Main Memory (RAM)**: Only large storage media that the CPU can access directly. Volatile.
- **Secondary Storage**: Extension of main memory (HDDs, SSDs). Non-volatile.

**Storage Hierarchy** (Fastest/Smallest -> Slowest/Largest):
1.  Registers
2.  Cache (L1, L2, L3)
3.  Main Memory
4.  Solid State Disk
5.  Magnetic Disk

## 1.3 Computer-System Architecture
- **Single-Processor Systems**: One main CPU. (Rare now).
- **Multiprocessor Systems (Parallel Systems)**:
    - **SMP (Symmetric Multiprocessing)**: All processors are peers; distinct L1/L2 caches but share physical memory.
    - **NUMA (Non-Uniform Memory Access)**: Accessing local memory is faster than remote memory.
- **Clustered Systems**: Multiple systems coupled together (e.g., via SAN). High availability.

## 1.4 Operating-System Operations
**Dual-Mode Operation**: To protect the OS from errant users.
1.  **User Mode**: Restricted access.
2.  **Kernel Mode**: Implementation of privileged instructions.
- A **System Call** triggers a software interrupt (trap), switching mode from User to Kernel.
