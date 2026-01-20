---
layout: page
title: "Networking Ch.5: Error Detection"
permalink: /courses/networking/ch5-error-detection/
---

# Chapter 5: Error Detection and Correction

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 5

The physical layer is imperfect. Signals get distorted. The Data Link Layer uses Error Detection and Correction to handle this.

## 5.1 Error-Correcting Codes (FEC)
We include enough redundant information to reconstruct the original data.
- **Hamming Distance**: The number of bit positions in which two codewords differ. To correct $d$ errors, you need a distance of $2d+1$.

### Hamming Codes
- positions that are powers of 2 ($1, 2, 4, 8...$) are check bits.
- Rest are data bits.
- Allows correcting a single bit error.

## 5.2 Error-Detecting Codes
Usually, it's more efficient to detect an error and ask for retransmission (ARQ) than to add massive redundancy for forward correction (FEQ), especially on reliable channels like fiber.

### Parity
- **Single Parity Bit**: Add 1 bit. Detects single bit errors. Failing rate 50%.

### Checksums
- Used in TCP/IP.
- Sum up data words (16-bit). Take 1s complement.
- Weak protection against systematic bursts.

### CRC (Cyclic Redundancy Check)
- View data string as a polynomial $M(x)$ with coefficients 0 and 1.
- Agreed upon Generator Polynomial $G(x)$.
- We append check bits such that the transmitted frame $T(x)$ is divisible by $G(x)$.
- **Receiver**: Divides received $T(x)$ by $G(x)$. Remainder $\ne 0 \implies$ Error.
- **Hardware**: Implemented efficiently using Shift Registers and XOR gates.
