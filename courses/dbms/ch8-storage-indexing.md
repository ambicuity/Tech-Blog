---
layout: page
title: "DBMS Ch.8: Storage & Indexing"
permalink: /courses/dbms/ch8-storage-indexing/
---

# Chapter 8: Overview of Storage and Indexing

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 8

How do we actually store data on disk?

## 8.1 Files and Access Methods
- **Heap File**: Random order. Slow to find things.
- **Sorted File**: Ordered by some field. Fast to search (Binary Search), slow to insert.
- **Index**: A data structure not unlike a library card catalog. Helps finding records without scanning.

## 8.2 Indexes
An index on a file speeds up selections on the **search key** fields.
- **Clustered Index**: The order of data records is the same as the order of data entries in the index. (Only 1 per table).
- **Unclustered Index**: Index entries are sorted, but point to random data pages. (Many per table).
- **Dense vs Sparse**:
    - Dense: Index entry for every data record.
    - Sparse: Index entry for one record per page.

## 8.3 Cost Models
We measure cost in **I/O Operations**.
- Scanning $N$ pages: $N$ I/Os.
- Binary Search: $\log_2 N$.
- Index lookup: Height of tree ($\sim 3-4$ I/Os).
