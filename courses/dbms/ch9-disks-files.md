---
layout: page
title: "DBMS Ch.9: Disks and Files"
permalink: /courses/dbms/ch9-disks-files/
---

# Chapter 9: Storing Data: Disks and Files

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 9

Database performance is dominated by I/O. We must understand the storage medium.

## 9.1 Memory Hierarchy
- **Primary Storage (RAM)**: Fast ($10^{-7}$ sec), Volatile, Expensive.
- **Secondary Storage (Disk)**: Slower ($10^{-2}$ sec), Non-volatile, Cheap.
- **Tertiary Storage (Tape)**: Archival.

## 9.2 Magnetic Disks
- **Platters** spin (RPM). **Heads** move in/out (Seek).
- **Access Time** = Seek Time + Rotational Delay + Transfer Time.
- **Seek Time**: Moving arm to correct Cylinder (~4-10ms). Dominates cost.
- **Rotational Latency**: Waiting for sector to rotate under head.

## 9.3 RAID (Redundant Arrays of Independent Disks)
- **RAID 0**: Striping (No redundancy). Fast read/write.
- **RAID 1**: Mirroring. Safe. Expensive.
- **RAID 5**: Striping with Parity using distributed parity blocks.

## 9.4 Disk Space Management
- DBSM manages space on disk as **Pages** (blocks), typically 4KB or 8KB.
- **Buffer Pool**: Cache of pages in RAM.
- **Replacement Policy**: LRU (Least Recently Used) or Clock.
