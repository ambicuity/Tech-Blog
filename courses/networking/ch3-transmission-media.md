---
layout: page
title: "Networking Ch.3: Transmission Media"
permalink: /courses/networking/ch3-transmission-media/
---

# Chapter 3: Guided Transmission Media

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 3

**Guided media** refers to physical channels where signals are confined to a specific path, such as copper wire or optical fiber. This contrasts with unguided media (wireless).

## 3.1 Twisted Pair
The oldest and most common transmission medium.
- Consists of two insulated copper wires twisted in a helical form.
- **Why twist?** The twisting cancels out electromagnetic interference (EMI) from external sources and crosstalk between neighboring pairs.

**Categories**:
- **Cat 3**: Old telephone lines.
- **Cat 5e**: Up to 1 Gbps. Tighter twists.
- **Cat 6/6a**: Up to 10 Gbps. Even tighter twists and thicker wires.

## 3.2 Coaxial Cable
Used for cable television and early Ethernet.
- Central copper core, insulating material, braided outer conductor (shield), plastic jacket.
- **Pros**: High bandwidth, excellent noise immunity.
- **Cons**: Bulky, expensive regarding installation.

## 3.3 Fiber Optics
Uses light pulses to transmit data. Standard for the backbone of modern networks.

### Structure
1.  **Core**: Ultra-thin glass where light travels.
2.  **Cladding**: Glass with lower refractive index to reflect light back into core.
3.  **Jacket**: Protective plastic.

### Light Sources
- **LED**: Used for Multimode fiber (short distance). Cheaper.
- **Semiconductor Laser**: Used for Single-mode fiber (long distance). Narrow beam, higher data rate.

### Comparison: Fiber vs. Copper
| Feature | Fiber | Copper |
| :--- | :--- | :--- |
| **Bandwidth** | Extremely High | Low to Moderate |
| **Distance** | Long (km) | Short (100m) |
| **Interference** | Immune (EM/RF) | Susceptible |
| **Security** | Hard to tap | Easy to tap |
| **Cost** | High | Low |

## 3.4 Power Line Communication (PLC)
Using electrical power wiring in a house for data traffic.
- Convenient (plugs everywhere).
- Noisy environment (motors, appliances switching on/off) makes it difficult to achieve high data rates reliably.
