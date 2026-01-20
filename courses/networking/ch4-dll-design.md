---
layout: page
title: "Networking Ch.4: Data Link"
permalink: /courses/networking/ch4-dll-design/
---

# Chapter 4: Data Link Layer Design Issues

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 4

The Data Link Layer (DLL) is responsible for efficient communication between two adjacent nodes managed by the same physical medium.

**Goals**:
1.  Provide a well-defined service interface to the Network Layer.
2.  Dealing with transmission errors.
3.  Regulating the flow of data so that slow receivers are not swamped by fast senders.

## 4.1 Services Provided to Network Layer
The DLL takes packets from the Network layer and encapsulates them into **frames** for transmission.

1.  **Unacknowledged Connectionless Service**: No connection, no ACKs. (Ethernet). Reliable delivery left to higher layers.
2.  **Acknowledged Connectionless Service**: No connection, but each frame is acknowledged. (WiFi).
3.  **Acknowledged Connection-Oriented Service**: Connection established. Frames guaranteed to be received exactly once and in right order.

## 4.2 Framing
The physical layer delivers a raw stream of bits. The DLL must break this into discrete frames.

**Methods**:
1.  **Byte Count**: Header field specifies number of bytes. (Dangerous if count is corrupted).
2.  **Flag Bytes with Byte Stuffing**: Start/End frames with a FLAG byte (e.g., `01111110`). If data contains FLAG, escape it.
3.  **Bit Stuffing**: If five consecutive 1s appear in data, sender inserts a 0. Receiver removes it.

## 4.3 Flow Control
Ensuring the sender doesn't drown the receiver.
- **Feedback-based**: Receiver sends back permission to send more (ACKs).
- **Rate-based**: Built-in limit on transmission rate.

**Sliding Window Protocols**:
- We usually maintain a "window" of frames the sender is allowed to send without waiting for an ACK.
- Improves efficiency on high-latency links.

## 4.4 Error Control
- **Error Correction** (FEC): Enough redundant info to reconstruct the data. (Hamming codes).
- **Error Detection**: Enough info to deduce that error occurred. (CRC - Cyclic Redundancy Check).
    - If error detected -> Request Retransmission (ARQ - Automatic Repeat reQuest).
