---
layout: page
title: "System Design Ch.5: Replication"
permalink: /courses/system-design/ch5-replication/
---

# Chapter 5: Replication

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 5

Replication means keeping a copy of the same data on multiple machines (replicas) that are connected via a network.
**Why?**
1.  High Availability (Keep working if one fails).
2.  Latency (Keep data geographically close to user).
3.  Scalability (Read throughput).

## 5.1 Leaders and Followers
How do we ensure all replicas have the same data? common solution: **Leader-based replication** (Master-Slave).
1.  One replica is the **Leader**. All **writes** must go to the leader.
2.  Other replicas are **Followers** (read replicas). They tail the leader's log.

### Synch vs. Asynch
- **Synchronous**: Leader waits for Follower ACK before reporting success to user.
    - *Pro*: Durability. *Con*: One slow follower halts the system.
- **Asynchronous**: Leader replies immediately.
    - *Pro*: Fast. *Con*: Data loss if leader crashes before replication.
- **Semi-synchronous**: One sync follower, rest async.

## 5.2 Problems with Replication Lag
In async replication, reading from a follower might return outdated data ("Time Travel").

### Consistency Models
1.  **Read-Your-Writes**: A user should always see data they just submitted. (Route user to Leader for their own profile).
2.  **Monotonic Reads**: A user should strictly see data moving forward in time, never backward. (Pin user to one replica).
3.  **Consistent Prefix Reads**: If a sequence of writes happens in a certain order, anyone reading them sees them in that order.

## 5.3 Multi-Leader Replication
Allow more than one node to accept writes.
- **Use Cases**: Multi-datacenter, Offline clients (Calendar app), Collaborative editing (Google Docs).
- **Cons**: Write Conflicts. If User A sets Title="A" in DC1 and User B sets Title="B" in DC2 simultaneously.
    - **Conflict Resolution**: Last Write Wins (LWW), Merging values.

## 5.4 Leaderless Replication
Dynamo-style (Amazon Dynamo, Cassandra, Riak).
- Client sends write to **all** replicas.
- **Quorum**: To read/write successfully, must get acknowledgement from $w$ and $r$ nodes such that $w + r > n$.
- **Sloppy Quorum**: If $n$ nodes are down, write to neighbors (hinted handoff).
