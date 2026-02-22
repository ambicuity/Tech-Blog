---
layout: page
title: DBMS for the AI Era
permalink: /courses/dbms/
---

## 🗄️ Foundations: Database Management Systems (The Cow Book)
*(Modern Supplements added for PostgreSQL Internals, LRU Clock Sweepers, and SSD Physics)*

This deep dive deconstructs traditional disk-based architectures to demonstrate the physical laws of Data Engineering and Crash Analytics.

---

## Chapter 1: Storage and The Buffer Manager

### 1.1 The Rigor: Disks and the Memory Hierarchy
A database engine spends $99\%$ of its architectural footprint orchestrating data movement between the mechanical/NAND disk and volatile CPU RAM. 

Disks are fundamentally partitioned into fixed-size **Pages** (blocks of 4KB or 8KB). A page is the absolute minimum geometry of data transfer. You cannot ask an SSD for 4 bytes of data; you must violently fetch the entire 8KB page into RAM across the PCIe bus.
The database maintains a **Buffer Pool** (a massive contiguous array in memory divided into Page Frames). If a query needs a row, the engine calculates the mathematical byte address, checks if the Page is resident in the Buffer Pool, and if not, executes an explicit, thread-blocking I/O Read.

### 1.2 Modern Application: The OOM Killer & Double Buffering
PostgreSQL implicitly embraces the surrounding OS environment via the **Linux Page Cache**. 
When Postgres flushes a dirty page to disk via `write()`, the Linux OS deliberately intercepts the call and caches the page again in Kernel memory. This creates **Double Buffering**. An 8KB page exists mathematically twice in physical RAM.

**Gotcha:** A junior engineer reads a blog that says "Databases love RAM!" and configures Postgres `shared_buffers` to $95\%$ of the physical EC2 instance memory. 
During a complex OLAP Hash Join, the Query Executor allocates temporary `work_mem` in the execution thread. Because the `shared_buffers` consumed the entire physical hardware limit, the AWS Linux Kernel exhausts RAM, deliberately triggers the **OOM (Out-of-Memory) Killer hardware exception**, and violently terminates the database engine via `SIGKILL`. System stability mathematically demands $60-70\%$ geometric buffer headroom.

### 1.3 Python Implementation: The Clock Replacement Algorithm
Standard LRU (Least Recently Used) is disastrous for databases. A single analytical Table Scan will rip through the disk, evicting the highly valuable root index pages from RAM just to flush useless sequential log data in. Database Engines use the **Clock Algorithm** (Second Chance).

A background "Clock Sweeper" rotates around the Buffer Frames array. If a frame has its `reference_bit` flagged `True` (it was recently queried), the Sweeper sets it to `False` (stripping its immunity) and moves on. If the Sweeper encounters a frame whose bit is *already* `False`, that frame is legally designated the victim, forcefully evicted, and the physical RAM address is overwritten.

---

## Chapter 2: Indexing and B+ Trees

### 2.1 The Rigor: The B+ Fanout Ratio
Searching an unindexed 1-Billion-row table demands a catastrophic $O(N)$ Sequential Disk Scan. 

A **B+ Tree**, an incredibly flat search tree, solves latency mathematically. 
Because an 8KB node is massive, a single B+ Tree node can hold roughly $200$ perfectly sorted pointers (**The Fanout Ratio**).
A tree with a fanout of $200$ and a height of $4$ can index exactly $1,600,000,000$ records. To find any user on Earth requires traversing exactly 4 localized nodes. Because the top 2 levels are physically tiny, the Buffer Manager permanently locks them in RAM. Finding a needle in 1.6 Billion haystack geometry requires exactly $2$ random Disk I/O reads.

### 2.2 The Engineer's Perspective: The Write Amplification of UUIDs
A team of developers enforces highly randomized UUID (v4) strings as their Primary Keys. Write Latency degrades by $900\%$. 

**Gotcha:** A Postgres B+ Tree *must* remain perfectly sorted.
When you use sequential integers (`AUTO_INCREMENT`), appended rows map perfectly to the far right leaf of the B+ Tree. The engine cleanly flushes one 8KB page and continues geometrically unharmed.
When adding truly randomized UUIDs, the engine is forced to insert the structural index key randomly into the *middle* of a fully-packed B+ Tree leaf node. The database must catastrophically execute a **Page Split**: it allocates a completely new 8KB page, fragments the existing records, repoints parental arrays, and flushes *multiple* disparate pages sequentially to disk. Avoid unstructured Primary Keys to protect the Sequential Write-Ahead Log.

---

## Chapter 3: Crash Recovery & ARIES

### 3.1 The Rigor: Write-Ahead Logging (WAL)
If a database crashes exactly 1 millisecond after an `UPDATE` acknowledges `200 OK` to an API, but before that dirty uncommitted page flushes to SSD, the data geometry evaporates.

To guarantee **Durability** (the 'D' in ACID), the database engine uses **Write-Ahead Logging**. 
The ironclad structural rule is: *The WAL log string must explicitly `fsync()` to persistent disk BEFORE the dirty memory page is legally allowed to be flushed to disk.*

### 3.2 The Engineer's Perspective: The `pg_wal` 500GB Bomb
You write a `cron` job backing up your WAL files to Amazon S3. Your API server locks up. You SSH in and discover `pg_wal/` has consumed 500 Gigabytes and the disk is technically zero bytes available.

**Gotcha:** To mathematically guarantee disaster recovery, PostgreSQL will never delete a sequential WAL generation file until the external `archive_command` explicitly returns a `0` exit code.
If your S3 script breaks silently, Postgres queues every single WAL file indefinitely spanning weeks, refusing to sacrifice your systemic integrity. When the EC2 Volume runs physically out of storage blocks, the Database categorically halts all active `UPDATE / INSERT` API queries globally rather than risking logical ACID violation. Database capacity is inextricably tied to architectural archiving logic.
