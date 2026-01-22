---
layout: page
title: "Arch Ch.2: Instructions"
permalink: /courses/architecture/ch2-instructions/
---

# Chapter 2: Instructions: Language of the Computer

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 2

The **Instruction Set Architecture (ISA)** is the contract between software and hardware. We focus on **MIPS** (or RISC-V), a typical RISC architecture.

## 2.1 Design Principles
1.  **Simplicity favors regularity**: All instructions are 32-bits long. All arithmetic uses 3 registers.
    - `add a, b, c`  # a = b + c
2.  **Smaller is faster**: Limit number of registers to 32 ($0-$31).
3.  **Good design demands good compromises**: Immediates (constants) are kept inside the instruction format to avoid memory access.

## 2.2 Operands
- **Registers**: Fast locations. `$s0-$s7` (saved), `$t0-$t9` (temporaries).
- **Memory**: Byte addressed.
    - **Load Word (lw)**: Memory $\to$ Register.
    - **Store Word (sw)**: Register $\to$ Memory.
    - Alignment restriction: Words must start at addresses divisible by 4.

## 2.3 Instruction Formats
- **R-Format**: `op | rs | rt | rd | shamt | funct` (Arithmetic).
- **I-Format**: `op | rs | rt | constant` (Loads/Stores/Branch/Immediates).
- **J-Format**: `op | address` (Jumps).

## 2.4 Logical Operations
- `sll` (Shift Left Logic): Multiply by $2^i$.
- `and` / `or`: Bitwise masking.

## 2.5 Procedures
Using the stack to support function calls.
- `jal` (Jump And Link): Saves PC+4 to `$ra` (Return Address).
- `jr $ra`: Jump to return address.
- **Spilling**: If we need more registers, we push old values to **Stack** (growing down in memory) and pop them later.
