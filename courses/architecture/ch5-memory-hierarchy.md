---
layout: page
title: "Arch Ch.5: Memory Hierarchy"
permalink: /courses/architecture/ch5-memory-hierarchy/
---

# Chapter 5: Large and Fast: Exploiting Memory Hierarchy

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 5

Programmers want unlimited amounts of fast memory.
**Reality**: Fast memory is expensive (SRAM). Cheap memory is slow (DRAM/Disk).
**Solution**: Hierarchy.

## 5.1 Principle of Locality
- **Temporal Locality**: Items accessed recently are likely to be accessed again soon (Loop variables).
- **Spatial Locality**: Items near those accessed recently are likely to be accessed soon (Arrays).

## 5.2 Caches
Small, fast memory that hides latency of main memory (RAM).
- **Direct Mapped Cache**: Each memory address maps to exactly one location in cache.
    - `(Block Address) modulo (Number of Blocks)`
- **Tags**: Stores high bits of address to identify *which* data is currently in the block.
- **Valid Bit**: Is this data meaningful?

## 5.3 Measuring Performance
$$ \text{AMAT} = \text{Hit Time} + \text{Miss Rate} \times \text{Miss Penalty} $$
- **Hit Time**: Access cache (~1 cycle).
- **Miss Penalty**: Fetch from RAM (~100 cycles).
- Even a 99% hit rate is crucial.

## 5.4 Associativity
- **Fully Associative**: Block can go anywhere.
- **Set Associative**: Block can go in one of $N$ places (N-way). Reduces conflict misses.
