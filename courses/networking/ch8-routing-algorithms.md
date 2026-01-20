---
layout: page
title: "Networking Ch.8: Routing"
permalink: /courses/networking/ch8-routing-algorithms/
---

# Chapter 8: Routing Algorithms

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 5 (Network Layer)

The main function of the Network Layer is **routing** packets from the source machine to the destination machine.

## 8.1 Desirable Properties
- **Correctness**: Packets get there.
- **Simplicity**: Easy to implement.
- **Robustness**: Router crashes shouldn't stop the network.
- **Stability**: Algorithms should converge (stop changing routes) quickly.
- **Fairness** vs. **Optimality**.

## 8.2 Shortest Path Routing (Dijkstra)
- Build a graph of the network.
- Edge weights can be hops, distance, physical bandwidth, delay, or cost.
- Dijkstra's algorithm finds the shortest path from Root to Every Node.
- Used in **OSPF (Open Shortest Path First)** and **IS-IS**. These are **Link State** protocols.

## 8.3 Distance Vector Routing (Bellman-Ford)
- Each router maintains a table (vector) giving the best known distance to each destination and which line to use to get there.
- Tables are updated by exchanging information with neighbors.
- **The Count-to-Infinity Problem**:
    - A down link is learned slowly. Good news travels fast; bad news travels slow.
    - Solved partially by **Split Horizon** (Don't tell X that you can reach Y via X).
- Used in **RIP (Routing Information Protocol)**.

## 8.4 Hierarchical Routing
As networks grow, routing tables get too big.
- Divide network into **Regions**.
- Routers know details of their region, but only "aggregate" direction for other regions.
- **Internet**:
    - **IGP (Interior Gateway Protocol)**: within an AS (Autonomous System). e.g., OSPF.
    - **EGP (Exterior Gateway Protocol)**: between ASes. e.g., **BGP (Border Gateway Protocol)**.

## 8.5 BGP (Border Gateway Protocol)
The protocol of the Internet availability.
- A **Path Vector** protocol (like Distance Vector, but tells you the full path of ASes: `AS1 -> AS5 -> AS3`).
- Prevents loops (if I see my AS in path, reject).
- Policy-based Routing (Politics/Economics over optimality).
