---
layout: page
title: "Networking Ch.10: Transport"
permalink: /courses/networking/ch10-transport-service/
---

# Chapter 10: The Transport Service

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 6 (Transport Layer)

The heart of the protocol hierarchy. The Transport Layer provides **end-to-end** communication services for applications.

## 10.1 Services Provided to Upper Layers
The goal: **Reliable, cost-effective data transport** from source machine to destination machine, independent of the physical network.
- **Transport Entity**: The code doing the work (part of OS kernel or library).
- **Socket**: The interface endpoint (`IP:Port`).

## 10.2 Transport Service Primitives
Standard `Berkeley Sockets` API:
1.  `SOCKET`: Create a new endpoint.
2.  `BIND`: Attach a local address (`Port`).
3.  `LISTEN`: Announce willingness to accept connections.
4.  `ACCEPT`: Block until connection attempt arrives.
5.  `CONNECT`: Attempt to establish connection.
6.  `SEND/RECEIVE`: Transfer data.
7.  `CLOSE`: Tear down connection.

## 10.3 Elements of Transport Protocols
The Transport Layer is similar to the Data Link Layer (Error control, Sequencing, Flow control), but easier in some ways (routers exist) and harder in others (packets can live a long time).

### Addressing
- How do we know which process to talk to? **Ports** (TSAP - Transport Service Access Point).
- Well-known ports: HTTP (80), SSH (22), SMTP (25).

### Connection Establishment
- **Three-Way Handshake**:
    - Crucial to prevent old duplicates (from a previous connection) from confusing the new one.
    - Alice $\to$ Bob: `SYN(seq=x)`
    - Bob $\to$ Alice: `SYN(seq=y), ACK(seq=x+1)`
    - Alice $\to$ Bob: `ACK(seq=y+1)`

### Connection Release
- **Asymmetric**: Phone call style. One hangs up, connection dead. (Data loss possible).
- **Symmetric**: Each side closes its direction separately (`FIN` packets). "I am done sending, but I can still listen".
