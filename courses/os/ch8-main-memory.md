---
layout: page
title: "OS Ch.8: Main Memory"
permalink: /courses/os/ch8-main-memory/
---

# Chapter 8: Main Memory

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 8

Memory consists of a large array of bytes, each with its own address. The CPU fetches instructions from memory according to the program counter.

## 8.1 Background
- **CPU Registers**: Accessed in 1 cycle.
- **Main Memory**: Accessed in many cycles (Stall).
- **Cache**: Fast memory between CPU and RAM.
- **Protection**: We must protect user processes from each other. (Base and Limit registers).

## 8.2 Swapping
A process must be in memory to be executed. If memory is full, a process can be **swapped** out to a backing store (disk) and brought back later.
- Context switch time becomes very high due to disk transfer rate.

## 8.3 Contiguous Memory Allocation
- **Fixed Partitioning**: Divide memory into static partitions. (Internal Fragmentation).
- **Dynamic Partitioning**: Allocate exactly what is needed. (External Fragmentation).
    - **First-Fit**: Allocate first hole that is big enough. (Fast).
    - **Best-Fit**: Allocate smallest hole that is big enough. (Slow, creates tiny useless holes).
    - **Worst-Fit**: Allocate largest hole.

## 8.4 Segmentation
A user view of memory. A program is a collection of segments (Main program, procedure, function, stack, symbol table).
- Address: `<segment-number, offset>`.

## 8.5 Paging
Physical address space of a process can be noncontiguous.
- **Frames**: Break physical memory into fixed-sized blocks (e.g., 4 KB).
- **Pages**: Break logical memory into blocks of same size.
- **Page Table**: Translates logical page numbers to physical frame numbers.
- **TLB (Translation Look-aside Buffer)**: Hardware cache for fast page table lookup.

**Fragmentation**:
- No External Fragmentation.
- **Internal Fragmentation**: Average of 1/2 page per process wasted.
