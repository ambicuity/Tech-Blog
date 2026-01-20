---
layout: page
title: "OS Ch.9: Virtual Memory"
permalink: /courses/os/ch9-virtual-memory/
---

# Chapter 9: Virtual Memory

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 9

Virtual Memory separates logical memory from physical memory.
**Key Idea**: Only part of the program needs to be in memory for execution.
**Benefit**:
- Logical address space can be much larger than physical address space ($2^{64}$ bytes).
- More processes can run concurrently.

## 9.1 Demand Paging
Bring a page into memory only when it is needed.
- **Valid-Invalid patterns**: Page table bit 'i' means page is not in memory (or invalid).
- **Page Fault**: Accessing a page marked 'i'.
    1.  Trap to OS.
    2.  Check if invalid reference (abort) or just not in memory.
    3.  Find free frame.
    4.  Read page from disk (swap space).
    5.  Modify page table (v).
    6.  Restart instruction.

## 9.2 Page Replacement Algorithms
If no free frame exists, we must evict a victim page. Which one?
1.  **FIFO**: Replace oldest page.
    - **Belady's Anomaly**: For some algorithms, adding more frames can cause *more* page faults.
2.  **Optimal**: Replace page that will not be used for longest period of time. (Impossible to implement, used as benchmark).
3.  **LRU (Least Recently Used)**: Replace page that has not been used for the longest period of time.
    - Good approximation of Optimal.
    - Implementation: Stack or Counters.

## 9.3 Thrashing
If a process does not have "enough" pages, the page-fault rate is very high. It spends more time paging than executing.
- CPU utilization drops.
- **Working-Set Model**: We try to keep the set of most active pages (Locality of Reference) in memory.
