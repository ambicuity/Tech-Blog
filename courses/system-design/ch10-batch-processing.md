---
layout: page
title: "System Design Ch.10: Batch Processing"
permalink: /courses/system-design/ch10-batch-processing/
---

# Chapter 10: Batch Processing

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 10

We distinguish three types of systems:
1.  **Services (Online)**: Wait for request, respond fast (SLA).
2.  **Batch Processing (Offline)**: Periodic, large input, high throughput.
3.  **Stream Processing (Near-Real-Time)**: Consume inputs as they appear.

## 10.1 MapReduce and Distributed Filesystems
Originally from Google (2004). Implemented in Hadoop.
- **HDFS (Hadoop Distributed File System)**: Shared-nothing. Replicates blocks (64MB or 128MB) for fault tolerance. NameNode tracks metadata.

### MapReduce
A programming framework to process data in HDFS.
1.  **Map**: Extract `(key, value)` pairs from input records.
2.  **Shuffle**: Framework sorts all pairs by key. All values for same key end up at same Reducer.
3.  **Reduce**: Iterate over values for a key, aggregate/produce output.

**Philosophy**:
- Move computation to data (run Mapper on the node where data lives).
- Immutable inputs.
- Idempotence (Re-run failed tasks safely).

## 10.2 Beyond MapReduce
MapReduce materializes intermediate state to disk (HDFS) between every job. Slow.

### Spark (Dataflow Engines)
Compute engines like Spark, Tez, and Flink treat the workflow as a DAG (Directed Acyclic Graph) of operators.
- **In-Memory**: Avoid writing to disk if possible.
- **RDD (Resilient Distributed Dataset)**: Abstraction for distributed collection.

### Graph Processing
- **Pregel (Google)** / **Giraph**: "Think like a vertex".
- **BSP (Bulk Synchronous Parallel)**: Computation proceeds in supersteps.
    1.  Compute.
    2.  Send messages to other vertices.
    3.  Barrier sync.
