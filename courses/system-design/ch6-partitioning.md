---
layout: page
title: "System Design Ch.6: Partitioning"
permalink: /courses/system-design/ch6-partitioning/
---

# Chapter 6: Partitioning

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 6

For very large datasets, replication is not enough; we need to break the data up into **partitions** (sharding).
**Goal**: Scalability. Different partitions can be placed on different nodes (Shared-Nothing architecture).

## 6.1 Partitioning Key-Value Data
How do we decide which record goes to which node?

### Random Partitioning
- **Pros**: Even data distribution.
- **Cons**: Impossible to find a record without querying all nodes.

### Partitioning by Key Range
Assign a continuous range of keys (e.g., A-F) to a partition.
- **Pros**: Efficient range queries.
- **Cons**: Hotspots. (e.g., Timestamps: all writes today go to the same partition).

### Partitioning by Hash of Key
Use a hash function (like MD5) on the key.
- **Pros**: Distributes data evenly (Consistent Hashing).
- **Cons**: Loses ability to do range queries efficiently.

## 6.2 Partitioning and Secondary Indexes
If you partition by Primary Key, how do you search by Secondary Index (e.g., search users by "color=red" when partitioned by UserID)?

1.  **Document-Partitioned Indexes (Local)**: Each partition maintains its own secondary index covering only its data ("Scatter-Gather").
2.  **Term-Partitioned Indexes (Global)**: A global index covers all data, but the index itself is partitioned. (Read is fast for single term, Write is complex/slow).

## 6.3 Rebalancing Partitions
When you add a new node, you want to move some data to it.
- **Don't use `mod N`**: Changing $N$ moves *almost all* keys.
- **Fixed number of partitions**: Create 1000 partitions. Move entire partitions to new node.
- **Dynamic partitioning**: Split partition when it exceeds size (HBase).
