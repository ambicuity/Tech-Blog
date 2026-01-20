---
layout: page
title: "Networking Ch.2: Physical Layer"
permalink: /courses/networking/ch2-theoretical-basis/
---

# Chapter 2: The Physical Layer

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 2

The physical layer is the foundation on which the network is built. It deals with transmitting raw bits over a communication channel.

## 2.1 The Theoretical Basis for Data Communication
Information can be transmitted on wires by varying some physical property such as voltage or current.

### Fourier Analysis
Any reasonably behaved periodic function $g(t)$ with period $T$ can be constructed as the sum of a (possibly infinite) number of sines and cosines.
- A signal is made of many frequencies.
- **Bandwidth**: The range of frequencies transmitted without being strongly attenuated.

### The Maximum Data Rate of a Channel
1.  **Nyquist Theorem** (Noiseless Channel):
    max data rate $= 2B \log_2 V$ bits/sec
    (where $B$ is bandwidth, $V$ is number of discrete levels).

2.  **Shannon's Theorem** (Noisy Channel):
    max data rate $= B \log_2 (1 + S/N)$ bits/sec
    (where $S/N$ is the signal-to-noise ratio).

## 2.2 Guided Transmission Media
### Magnetic Media
- Tapes. High bandwidth (truckload of tapes), high latency.

### Twisted Pair
- Two insulated copper wires twisted together to reduce electrical interference.
- **Cat5e/Cat6**: specific standards for thickness/twisting. Used in Ethernet.

### Coaxial Cable
- Better shielding than twisted pair. Used for Cable TV/Internet.

### Fiber Optics
- Transmission of light through glass.
- **Physics**: Data travels at speed of light in glass ($\approx 2/3 c$). Based on **Total Internal Reflection**.
- **Single-mode**: Thin core, laser light, long distance (100km).
- **Multi-mode**: Thicker core, LED light, short distance (LANs).

## 2.3 Wireless Transmission
- **The Electromagnetic Spectrum**: Radio, Microwave, Infrared, Light.
- **Frequency Hopping (FHSS)**: Hopping between frequencies to avoid interference (used in Bluetooth).
- **Direct Sequence (DSSS)**: Spreading signal over wide band (used in old WiFi).

## 2.4 Communication Satellites
1.  **GEO** (Geostationary): 35,000km up. Fixed spot in sky. High latency (~270ms).
2.  **LEO** (Low Earth Orbit): < 1,500km. Starlink/Iridium. Low latency but requires constellation of moving satellites.
