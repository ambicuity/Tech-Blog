---
layout: page
title: "System Design Ch.9: Consistency"
permalink: /courses/system-design/ch9-consistency-consensus/
---

# Chapter 9: Consistency and Consensus

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 9

Consensus is one of the most important and difficult problems in distributed systems: getting several nodes to agree on something (e.g., who is the leader?).

## 9.1 Consistency Guarantees
- **Linearizability** (Strong Consistency): System appears as if there is only one copy of the data and all operations are atomic.
    - If User A reads $x=1$, User B must typically read $x=1$ (or newer).
    - CAP Theorem: In presence of partitions (P), you must choose between Linearizability (C) and Availability (A).

## 9.2 Ordering and Causality
- **Causal Consistency**: Events that are causally related must be seen in the same order by everyone. Concurrent events can be seen in any order. (Weaker than Linearizability, but more available).
- **Lamport Timestamps**: $(counter, nodeID)$. Provides a total ordering consistent with causality.

## 9.3 Distributed Consensus
Algorithms to decide on a value.
**Equivalent Problems**:
- Linearizable Log (Blockchain).
- Total Order Broadcast.
- Leader Election.

### Algorithms
1.  **Paxos**: The classic algorithm (Leslie Lamport). Very hard to implement.
2.  **Raft**: Designed to be understandable. Uses Leader Election + Log Replication.
    - Nodes: Leader, Follower, Candidate.
    - **Term**: Logical time.
    - **Election**: If follower hears nothing, it becomes Candidate and requests votes.

### Two-Phase Commit (2PC)
Used for atomic transactions across multiple databases.
1.  **Prepare Phase**: Coordinator asks all participants: "Can you commit?". Participants lock resources.
2.  **Commit Phase**: If everyone said YES, Coordinator says "COMMIT". If anyone said NO, Coordinator says "ABORT".
- **Blocking**: If coordinator crashes, participants are stuck holding locks.
