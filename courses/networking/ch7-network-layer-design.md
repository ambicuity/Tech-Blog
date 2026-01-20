---
layout: page
title: "Networking Ch.7: Network Layer"
permalink: /courses/networking/ch7-network-layer-design/
---

# Chapter 7: Network Layer Design Issues

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 5 (Network Layer)

The Network Layer allows end-to-end delivery of packets across multiple networks (the internetwork).

## 7.1 Store-and-Forward Packet Switching
A host transmits a packet to the nearest router. The router receives the entire packet, verifies checksum, looks up routing table, and forwards to the next router.

## 7.2 Services Provided to Transport Layer
The Debate:
1.  **Connection-Oriented (Virtual Circuits)**: Setup path first. Packets follow same path. (ATM, MPLS). Reliability in network.
    - Router memory needed for state.
2.  **Connectionless (Datagrams)**: Packets routed independently. (IP). Reliability in host.
    - Robust (routers can crash).
    - **Internet chose this**.

## 7.3 Routing Algorithms
The Brains of the network. Deciding which output line an incoming packet goes to.

### 1. Shortest Path Routing (Dijkstra)
- Graph of nodes and weighted edges (latency/bandwidth).
- Find shortest path from Self to All.
- Used in OSPF (Link State).

### 2. Distance Vector Routing (Bellman-Ford)
- Each router knows "distance to X" via each neighbor.
- Tells neighbors: "I can reach X in 5 hops".
- **Count-to-Infinity Problem**: Bad news travels slowly.
- Used in RIP.

## 7.4 Congestion Control
When too many packets act at once, performance degrades (collapse).
- **Traffic Shaping**: Leaky Bucket / Token Bucket algorithms to smooth out bursts.
- **Choke Packets**: Router tells sender "Slow down!".
- **Load Shedding**: Drop packets (Random Early Detection - RED).
