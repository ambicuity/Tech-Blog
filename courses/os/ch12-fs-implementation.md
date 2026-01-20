---
layout: page
title: "OS Ch.12: FS Implementation"
permalink: /courses/os/ch12-fs-implementation/
---

# Chapter 12: File-System Implementation

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 12

How do we implement the file system concepts (files, directories) on physical storage (blocks)?

## 12.1 File-System Structure
- **Logical File System**: Manages metadata (inodes).
- **File-Organization Module**: Maps logical blocks (0..N) to physical blocks.
- **Basic File System**: Generic commands to read/write physical blocks.
- **I/O Control**: Device drivers.

## 12.2 Allocation Methods
How do we allocate space for a file?
1.  **Contiguous Allocation**: File occupies a set of contiguous blocks.
    - Fast (min seek).
    - Fragmentation drawback. Hard to grow files.
2.  **Linked Allocation**: Each block points to the next.
    - No external fragmentation. Easy to grow.
    - Slow random access (must traverse list).
    - **FAT (File Allocation Table)**: Move pointers to a separate table in RAM. (Used by MS-DOS/USB keys).
3.  **Indexed Allocation (Unix Inodes)**:
    - Bring all pointers together into an index block (**inode**).
    - Direct blocks + Single Indirect + Double Indirect + Triple Indirect.
    - Supports small and huge files efficiently.

## 12.3 Free-Space Management
- **Bit Vector**: 1 bit per block. (0=free, 1=occupied). Efficient to find first free block.
- **Linked List**: Head pointer to first free block.

## 12.4 Recovery
- **Consistency Checking (`fsck`)**: Scans disk to compare metadata (directory structure) with state of blocks (free/used) and fixes inconsistencies. Slow.
- **Journaling (Log-Structured File Systems)**:
    - Record metadata changes to a sequential log (Journal) *before* applying.
    - Recovering from crash is fast: just replay the log.
    - Used in **ext4**, **NTFS**, **XFS**.
