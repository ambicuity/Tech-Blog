---
layout: page
title: "Arch Ch.5: Memory Hierarchy"
permalink: /courses/architecture/ch5-memory-hierarchy/
---

# Chapter 5: Exploiting Memory Hierarchy (Caches)

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 5

We want a memory that is unlimited in size and effectively instantaneous.
*   **SRAM (Cache)**: Fast ($< 1$ns), Expensive.
*   **DRAM (Main Memory)**: Slow ($~50$ns), Cheap.
*   **Disk/SSD**: Very Slow, very cheap.

## 5.1 Direct Mapped Cache
Each memory address maps to exactly **one** location in the cache.
$$ \text{Cache Index} = (\text{Block Address}) \pmod{\text{Num Blocks}} $$

### Analyzing an Address
For a 32-bit address and a 16KB Cache with 4-byte blocks (Total blocks = $16KB / 4B = 4096 = 2^{12}$):
1.  **Byte Offset** (2 bits): Which byte in the word? (0-3).
2.  **Index** (12 bits): Which block in the cache? ($0-4095$).
3.  **Tag** (18 bits): Remaining upper bits.

### The Access Protocol
1.  Use **Index** to go to one specific slot.
2.  Check **Valid Bit**. If 0, Miss.
3.  Compare **Tag** in cache with Tag in address.
    -   **Match**: **Hit**. Return Data.
    -   **Mismatch**: **Miss**. Fetch from DRAM.

---

## 5.2 Handling Misses
1.  **Stall** the CPU pipeline.
2.  Fetch block from lower level (RAM). Use high-bandwidth burst mode.
3.  Write block into Cache. Set Valid=1, Tag=AddressTag.
4.  Restart instruction.

## 5.3 Set Associative Cache
Direct Mapped suffers from **Conflict Misses** (Ping-pong effect if two active variables map to same index).
**N-way Set Associative**: Each block can go into any of $N$ slots in a specific Set.
$$ \text{Set Index} = (\text{Block Address}) \pmod{\text{Num Sets}} $$
-   Search all $N$ tags in parallel.
-   **Replacement Policy**: Which of the $N$ blocks to evict? **LRU** (Least Recently Used).

---

## 5.4 Performance Math
$$ \text{AMAT} = \text{Hit Time} + \text{Miss Rate} \times \text{Miss Penalty} $$

**Example**:
-   Hit Time = 1 cycle.
-   Miss Penalty = 100 cycles.
-   Miss Rate = 5%.
-   $AMAT = 1 + 0.05 \times 100 = 6$ cycles.
-   *Conclusion*: Hardware is 6x slower than ideal due to memory! Reducing Miss Rate is critical.

## 5.5 Virtual Memory
Extends the hierarchy to Disk.
-   **Page Table**: Maps Virtual Address $\to$ Physical Address.
-   **TLB (Translation Lookaside Buffer)**: A special "Cache" for the Page Table itself. Critical for performance.
-   **Page Fault**: When data is not in RAM. OS traps, loads from disk. Very slow ($10^6$ cycles). Context Switch usually happens.
