---
layout: page
title: "Arch Ch.2: Instructions"
permalink: /courses/architecture/ch2-instructions/
---

# Chapter 2: Instructions: Language of the Computer

> **Reference**: *Computer Organization and Design* by Patterson & Hennessy, Chapter 2

The MIPS ISA.

## 2.1 MIPS Fields
All instructions 32-bit.
**R-Type** (Register): `add $t0, $s1, $s2`.
-   `Op(6) | Rs(5) | Rt(5) | Rd(5) | Shamt(5) | Funct(6)`

**I-Type** (Immediate): `lw $t0, 32($s3)`.
-   `Op(6) | Rs(5) | Rt(5) | Imm(16)`

**J-Type** (Jump): `j 1000`.
-   `Op(6) | Address(26)`

## 2.2 Addressing Modes
1.  **Register**: Operand in register.
2.  **Base**: Operand at `Reg + Imm` (Memory).
3.  **Immediate**: Constant in instruction.
4.  **PC-Relative**: `PC + 4 + Imm` (Branch).
5.  **Pseudo-Direct**: `PC[31:28] | Address | 00` (Jump).

## 2.3 Stored Program Concept
Instructions are just data in memory. We can build compilers, linkers, loaders.
