---
layout: page
title: "System Design Ch.3: Storage"
permalink: /courses/system-design/ch3-storage-retrieval/
---

# Chapter 3: Storage and Retrieval

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 3

Fundamental to any database is the mechanism it uses to store data on disk and find it again.

## 3.1 Data Structures That Power Your Database
Consider the world's simplest database: two Bash functions.
```bash
db_set () { echo "$1,$2" >> database; }
db_get () { grep "^$1," database | sed -e "s/^$1,//" | tail -n 1; }
```
- **Write**: Append-only log ($O(1)$). Very fast.
- **Read**: $O(n)$. Linearly scan the whole file. Very slow.

To speed up reads, we need an **Index**.

### Hash Indexes
Keep an in-memory hash map where `key` = primary key and `value` = byte offset in the file.
- Used by **Bitcask** (Riak).
- **Pros**: Very fast reads ($O(1)$) and writes.
- **Cons**: Keys must fit in RAM. No range queries.

### SSTables and LSM-Trees
**SSTable (Sorted String Table)**: Key-value pairs in the log are sorted by key.
- **LSM-Tree (Log-Structured Merge-Tree)**:
    1.  Writes go to an in-memory balanced tree (**MemTable**).
    2.  When MemTable is full, flush to disk as an **SSTable** segment.
    3.  Reads check MemTable, then recent segments, then older segments.
    4.  **Compaction**: Background process merges segments and discards deleted keys.
- Used by **LevelDB**, **RocksDB**, **Cassandra**, **HBase**.
- **Pros**: High write throughput (turns random writes into sequential writes).

### B-Trees
The most widely used indexing structure (SQL dbs).
- Broken down into fixed-size **pages** (usually 4KB).
- A tree of pages. Queries start at root and traverse down to leaf.
- **Branching Factor**: Number of child references in a page (typically hundreds).
- **Wal (Write-Ahead Log)**: Used to restore B-Tree after crash.

## 3.2 Transaction Processing or Analytics?
- **OLTP (Online Transaction Processing)**: User-facing, low latency, small queries. (Row-oriented storage is detailed).
- **OLAP (Online Analytic Processing)**: Business intelligence, heavy aggregates.
- **Data Warehouses**: Specialized OLAP databases (Redshift, Snowflake).

### Column-Oriented Storage
For OLAP, storing data by **column** instead of row allows efficient compression (Run-Length Encoding) and vectorization.
