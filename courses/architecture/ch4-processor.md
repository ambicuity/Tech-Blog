---
layout: page
title: "Arch Ch.4: The Processor"
permalink: /courses/architecture/ch4-processor/
---

# Chapter 4: The Processor

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 4

How do we build the hardware to execute MIPS instructions?

## 4.1 Datapath and Control
- **Datapath**: Elements that process data (Registers, ALU, Muxes).
- **Control**: Logic that commands the datapath (signals which Mux line to select, ALU operation, Write assertion).

## 4.2 Pipelining
The assembly line analogy. Break instruction execution into 5 stages:
1.  **IF**: Instruction Fetch.
2.  **ID**: Instruction Decode / Reg Read.
3.  **EX**: Execute / Address Calc.
4.  **MEM**: Memory Access.
5.  **WB**: Write Back.

**speedup**: Ideal speedup is 5x.
**Clock Cycle**: determined by longest stage.

## 4.3 Hazards
Pipelining works great until...
1.  **Structural Hazard**: Hardware cannot support combination (e.g., Fetch and Mem access use same port).
2.  **Data Hazard**: Instruction depends on result of previous one still in pipeline.
    - Solution: **Forwarding** (Bypassing). Feed ALU result directly to next ALU input.
3.  **Control Hazard**: Branching. We don't know PC until stage 3, but we must fetch next instruction now.
    - Solution: **Branch Prediction**.
    - **Flush**: If wrong, throw away instructions in pipeline.
