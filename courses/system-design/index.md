---
layout: page
title: System Design
permalink: /courses/system-design/
role: course-index
---

# System Design

> **Core Text**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann.

This course explores the principles and patterns for building reliable, scalable, and maintainable software systems, with a focus on distributed data systems.

## Syllabus

### Part I: Foundations of Data Systems
- [**Chapter 1: Reliable, Scalable, and Maintainable Applications**](/courses/system-design/ch1-reliability-scalability-maintainability/)
- [**Chapter 2: Data Models and Query Languages**](/courses/system-design/ch2-data-models/)
- [**Chapter 3: Storage and Retrieval**](/courses/system-design/ch3-storage-retrieval/) (Log-Structured vs. B-Trees)
- [**Chapter 4: Encoding and Evolution**](/courses/system-design/ch4-encoding-evolution/) (Avro, Protobuf, Thrift)

### Part II: Distributed Data
- [**Chapter 5: Replication**](/courses/system-design/ch5-replication/) (Leader-based, Multi-leader, Leaderless)
- [**Chapter 6: Partitioning**](/courses/system-design/ch6-partitioning/)
- [**Chapter 7: Transactions**](/courses/system-design/ch7-transactions/) (ACID, Isolation Levels)
- [**Chapter 8: The Trouble with Distributed Systems**](/courses/system-design/ch8-distributed-trouble/) (Clocks, Split Brains)
- [**Chapter 9: Consistency and Consensus**](/courses/system-design/ch9-consistency-consensus/) (Paxos, Raft, Two-Phase Commit)

### Part III: Derived Data
- [**Chapter 10: Batch Processing**](/courses/system-design/ch10-batch-processing/) (MapReduce, Spark)
- [**Chapter 11: Stream Processing**](/courses/system-design/ch11-stream-processing/) (Kafka, Flink)
