---
layout: page
title: "Networking Ch.9: Congestion"
permalink: /courses/networking/ch9-congestion-control/
---

# Chapter 9: Congestion Control Algorithms

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 5 (Network Layer)

**Congestion**: When too many packets act are present in (a part of) the subnet, performance degrades.

## 9.1 Principles of Congestion Control
- **Congestion vs. Flow Control**:
    - Flow Control: Point-to-point (Fast sender/Slow receiver).
    - Congestion Control: Global issue (Too much traffic in network).
- **Congestion Collapse**: When carried load drops because delays cause retransmissions, adding more load.

## 9.2 Approaches
1.  **Open Loop**: Prevention. Design the system to avoid congestion (good when traffic is predictable).
2.  **Closed Loop**: Feedback. Monitor system, detect congestion, tell senders to slow down.

## 9.3 Traffic Shaping
Regulating the average rate and burstiness of data transmission.
- **Leaky Bucket Algorithm**:
    - Water enters a bucket at varying rates.
    - Water leaks out at a constant rate (via a hole).
    - Hard limit on output rate. Smoothes bursty traffic.
- **Token Bucket Algorithm**:
    - Tokens added to bucket at constant rate.
    - To send a packet, you need to grab a token.
    - Allows bursts (up to bucket size).

## 9.4 Feedback Methods
1.  **Choke Packets**: Router sends a packet back to source saying "I'm congested". Source reduces rate.
2.  **ECN (Explicit Congestion Notification)**: Router marks a bit in the IP header. Destination sees bit and tells source in the ACK.
3.  **Load Shedding**: Just drop packets.
    - **Tail Drop**: Drop new packets when queue is full.
    - **RED (Random Early Detection)**: Start dropping packets randomly *before* queue is full to warn TCP senders.

## 9.5 TCP Congestion Control
The internet relies on hosts to control congestion.
- **Slow Start**: Start with window = 1. Double every RTT (Exponential growth).
- **Congestion Avoidance**: When threshold is reached, grow linearly.
- **packet loss** is the signal of congestion.
