---
layout: page
title: "Arch Ch.4: The Processor"
permalink: /courses/architecture/ch4-processor/
---

# Chapter 4: The Processor (Pipelining)

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 4

The performance of a CPU is determined by the **Throughput** of interactions. Pipelining is the key technique used to make fast CPUs which overlaps the execution of instructions.

## 4.1 The MIPS Pipeline Stages
The standard RISC pipeline has 5 stages. Each stage takes 1 clock cycle.

1.  **IF (Instruction Fetch)**:
    -   Read instruction from Instruction Memory at address PC.
    -   $PC \leftarrow PC + 4$.
2.  **ID (Instruction Decode)**:
    -   Read register values ($rs, rt$) from Register File.
    -   Sign-extend immediate values.
3.  **EX (Execute / Address Calc)**:
    -   ALU calculates result (for arithmetic) or memory address (for Load/Store).
    -   For Branch: Calculate target address.
4.  **MEM (Memory Access)**:
    -   Read/Write Data Memory (only for `lw`, `sw`).
5.  **WB (Write Back)**:
    -   Write result (from ALU or Memory) back into Register File.

### Performance Ideal
In an ideal pipeline, we finish 1 instruction every cycle (CPI = 1).
$$ \text{Speedup} = \frac{\text{Pipeline Depth}}{\text{1}} = 5x $$

---

## 4.2 Hazards
Hazards prevent the next instruction from executing in the very next cycle.

### 1. Structural Hazards
Hardware resource conflict.
*   *Example*: If we had only one memory for both Instructions and Data. IF stage and MEM stage would collide.
*   *Solution*: Split L1 Cache into I-Cache and D-Cache (Harvard Architecture).

### 2. Data Hazards (Read-After-Write)
An instruction depends on the result of a previous instruction that hasn't been written back yet.
```assembly
add $s0, $t0, $t1   # Writes $s0 in WB stage (Cycle 5)
sub $t2, $s0, $t3   # Reads $s0 in ID stage (Cycle 2) -> ERROR! Old value.
```
*   **Solution A: Stalling (Bubbles)**. The hardware inserts `nop` instructions. Wastes cycles.
*   **Solution B: Forwarding (Bypassing)**.
    -   The result of `add` is available at the end of EX stage (Cycle 3).
    -   Hardware "wires" the ALU Output of Cycle 3 directly to the ALU Input of Cycle 4 (for the `sub`).
    -   Eliminates stall!

### 3. Control Hazards (Branching)
The decision to branch (change PC) isn't known until the MEM stage (or EX stage). By then, we have already fetched the next 2-3 instructions.
*   **Solution A: Stall**. Wastes 3 cycles on every branch.
*   **Solution B: Branch Prediction**.
    -   **Static**: Always predict "Not Taken".
    -   **Dynamic**: Keep a history table (Branch History Table). If branch is taken, remember it.
    -   If prediction is wrong: **Flush** pipeline (turn instructions into bubbles).

---

## 4.3 Exceptions and Interrupts
What happens when `add` overflows or user hits `Ctrl+C`?
-   We cannot just stop.
-   We must save the address of the offending instruction to **Exception Program Counter (EPC)**.
-   Jump to the OS Exception Handler.
-   Flush instructions following the bad one. (Exact Exception).

## 4.4 Advanced ILP
To go beyond CPI=1 (Superscalar), we must issue multiple instructions per cycle.
-   **Static Multiple Issue (VLIW)**: Compiler bundles instructions.
-   **Dynamic Multiple Issue**: Hardware scheduler (Tomasulo's Algorithm) reorders instructions at runtime (Out-of-Order Execution).
