---
layout: page
title: "Networking Ch.11: Protocols"
permalink: /courses/networking/ch11-transport-protocols/
---

# Chapter 11: Transport Protocols (TCP/UDP)

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 6 (Transport Layer)

The Internet transmits streams of bytes using two main protocols.

## 11.1 UDP (User Datagram Protocol)
"Connectionless Transport".
- Nothing more than an IP packet with a short header adding source/dest **Ports** and a checksum.
- **Properties**: Unreliable, Unordered, No flow control, lightweight.
- **Uses**: DNS, VoIP (Video/Audio), Online Gaming, RPC.
- **Rationale**: Better to drop a video frame than pause everything to wait for a retransmission.

## 11.2 TCP (Transmission Control Protocol)
"Reliable Byte Stream".
- **Properties**: Reliable, In-order, Flow-controlled, Congestion-controlled.
- **Header**: Source/Dest Port, Sequence Num, Ack Num, Window Size, Checksum, Flags (`SYN`, `ACK`, `FIN`, `RST`).

### TCP Service Model
- Stream of bytes, not messages. (Receiver might read 100 bytes in two chunks of 50).
- **Nagle's Algorithm**: Buffers tiny packets to prevent overhead ("Silly Window Syndrome").

### Comparison: TCP vs UDP
| Feature | TCP | UDP |
| :--- | :--- | :--- |
| **Reliability** | Guaranteed | Best Effort |
| **Ordering** | Guaranteed | None |
| **Connection** | Heavy (Handshake) | None |
| **Overhead** | High (20 bytes+) | Low (8 bytes) |
| **Speed** | Slower (ACKS) | Faster |

## 11.3 TCP Reliability Implementation
- **ARQ (Automatic Repeat reQuest)**: Sender sets timer. If no ACK by timeout, resend.
- **Fast Retransmit**: If sender gets 3 duplicate ACKs for packet $N$, it infers $N+1$ is lost and resends immediately without waiting for timeout.
- **Flow Control**: Receiver advertises `WindowSize` (bytes buffer available). Sender ensures `FlightSize < WindowSize`.
