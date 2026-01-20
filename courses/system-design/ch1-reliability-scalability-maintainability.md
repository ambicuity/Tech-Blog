---
layout: page
title: "System Design Ch.1: Foundations"
permalink: /courses/system-design/ch1-reliability-scalability-maintainability/
---

# Chapter 1: Reliable, Scalable, and Maintainable Applications

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 1

In the modern era, most applications are *data-intensive* rather than *compute-intensive*. The bottleneck is the amount of data, the complexity of data, and the speed at which it changes.

Three main concerns dominate data system design:

## 1. Reliability
The system should continue to work correctly (performing the correct function at the desired level of performance) even in the face of adversity (hardware or software faults, and even human error).

- **Fault vs. Failure**: A *fault* is a component deviating from spec (e.g., HDD crash). A *failure* is the system stopping service to the user. We design fault-tolerant systems to prevent faults from causing failures.
- **Chaos Engineering**: Intentionally inducing faults (like Netflix's Chaos Monkey) to test resilience.

## 2. Scalability
As the system grows (in data volume, traffic volume, or complexity), there should be reasonable ways of dealing with that growth.

### Describing Load
Load is described by **load parameters**.
- **Twitter Example**:
    - Post tweet: 4.6k req/sec (12k peak).
    - Home timeline: 300k req/sec.
    - **Fan-out**: The challenge is delivering a tweet to all followers.
    - *Approach 1 (Pull)*: Query DB when user loads feed. (Expensive read)
    - *Approach 2 (Push)*: Fan-out write to every follower's cache on tweet. (Expensive write for celebrities like Justin Bieber).
    - *Hybrid*: Push for normal users, Pull for celebrities.

### Latency vs. Response Time
- **Response Time**: What the client sees (processing time + network delay + queuing delay).
- **Latency**: Duration that a request is waiting to be handled (awaiting service).
We focus on percentiles: p50 (median), p95, p99 (tail latency).

## 3. Maintainability
Over time, many different people will work on the system (engineering and operations), and they should all be able to work on it productively.

- **Operability**: Making it easy for operations teams to keep the system running smoothly.
- **Simplicity**: Managing complexity. Removing accidental complexity through good abstractions.
- **Evolvability**: Making it easy to make changes to the system in the future (Extensibility).
