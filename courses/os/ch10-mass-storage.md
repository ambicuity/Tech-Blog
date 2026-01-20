---
layout: page
title: "OS Ch.10: Mass-Storage"
permalink: /courses/os/ch10-mass-storage/
---

# Chapter 10: Mass-Storage Structure

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 10

The file system usually resides permanently on secondary storage.

## 10.1 Hard Disk Drives (HDD)
- **Platters**: Magnetic disks spinning at 5400/7200 RPM.
- **Read-Write Head**: Flies just above the surface.
- **Seek Time**: Move arm to correct cylinder (~4ms).
- **Rotational Latency**: Wait for sector to rotate under head (~3ms).
- **Scheduling**:
    - **FCFS**: Simple but slow.
    - **SSTF (Shortest Seek Time First)**: Greedy. Can cause starvation.
    - **SCAN (Elevator)**: Arm moves end-to-end.
    - **C-SCAN**: Circular SCAN. Treat cylinders as a circular list.

## 10.2 Nonvolatile Memory (NVM) / SSD
- **Flash Memory (NAND)**: No moving parts.
- **FTL (Flash Translation Layer)**: Maps logical blocks to physical pages. Handles **Garbage Collection** (erasing blocks) and **Wear Leveling** (distributing writes so cells die evenly).
- Algorithm: FCFS is usually fine because no seek time. Merging writes is beneficial.

## 10.3 RAID Structure
**Redundant Array of Independent Disks**.
- **RAID 0**: Striping. No redundancy. Fast.
- **RAID 1**: Mirroring. 100% redundancy. Safe but expensive.
- **RAID 5**: Block-Interleaved Parity. Parity distributed across drives. Can survive 1 failure.
- **RAID 6**: Two parities. Can survive 2 failures.
- **RAID 10**: Stripe of Mirrors.

## 10.4 Stable-Storage Implementation
To guarantee writes are never lost (even during a crash during write):
- Replicate info on multiple disks with independent failure modes.
- **Successful Completion**: Only if all copies written.
- **Partial Failure**: Restore from good copy.
