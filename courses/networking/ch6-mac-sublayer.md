---
layout: page
title: "Networking Ch.6: MAC Sublayer"
permalink: /courses/networking/ch6-mac-sublayer/
---

# Chapter 6: The Medium Access Control (MAC) Sublayer

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 4 (MAC)

In shared broadcast channels (like WiFi or Ethernet Bus), we need a protocol to decide who gets to talk next. That is the MAC sublayer (bottom part of Data Link Layer).

## 6.1 Channel Allocation Problem
- **Static**: FDM (Frequency Division) or TDM (Time Division). Inefficient for bursty traffic.
- **Dynamic**: ALOHA, CSMA.

## 6.2 Multiple Access Protocols
### ALOHA
- **Pure ALOHA**: Transmit whenever you have data. If collision, wait random time and retry. Efficiency: 18%.
- **Slotted ALOHA**: Transmit only at start of time slots. Efficiency: 36%.

### CSMA (Carrier Sense Multiple Access)
"Listen before you talk".
- **CSMA/CD (Collision Detection)**: Used in Ethernet.
    - Listen. If busy, wait.
    - If idle, transmit.
    - If collision detected while transmitting, stop, jam signal, and wait random time (Binary Exponential Backoff).
- **CSMA/CA (Collision Avoidance)**: Used in WiFi.
    - Because we can't detect collisions easily on radio (hidden terminal problem), we try to avoid them (RTS/CTS).

## 6.3 Ethernet (IEEE 802.3)
- **Classic Ethernet**: Coax cable (Bus).
- **Switched Ethernet**: Hubs replaced by **Switches**. No collisions anymore (each port is a collision domain).
- **Frame Format**: Preamble, Dest MAC, Src MAC, Type, Data, CRC.
- **MAC Address**: 48-bit unique ID (e.g., `00:1A:2B:3C:4D:5E`).

## 6.4 Wireless LANs (802.11 WiFi)
- **Hidden Station Problem**: A can hear B, C can hear B, but A and C cannot hear each other. If both send to B, collision.
- **Solution**: MACA (Multiple Access with Collision Avoidance).
    - Sender requests **RTS** (Request to Send).
    - Receiver replies **CTS** (Clear to Send).
    - Neighbors hear CTS and stay silent.
