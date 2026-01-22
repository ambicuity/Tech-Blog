---
layout: page
title: "Compilers Ch.7: Run-Time"
permalink: /courses/compilers/ch7-runtime-environments/
---

# Chapter 7: Run-Time Environments

> **Reference**: *Compilers* (Dragon Book), Chapter 7

The compiler considers the program as a static text. The **Runtime System** manages the execution.

## 7.1 Storage Organization
Memory is divided into:
- **Code**: Text (Instructions).
- **Static**: Global variables.
- **Heap**: Dynamic memory (`malloc`, `new`).
- **Stack**: Function call activations.

## 7.2 Stack Allocation
Each function call creates an **Activation Record** (Frame).
- Contains: Parameters, Return Address, Saved Registers, Local Variables.
- **Frame Pointer (FP)**: Points to base of current frame.
- **Stack Pointer (SP)**: Points to top of stack.
- When function returns, SP is reset to FP.

## 7.3 Access to Non-Local Data
- **Static Scope**: In Pascal/Ada (nested functions), can access variables of enclosing function.
- **Access Link (Static Link)**: Pointer to the frame of the enclosing function.

## 7.4 Heap Management
- **Garbage Collection**: Automatically reclaiming unused memory.
- **Mark-and-Sweep**: Stop the world. Traverse from roots. Mark reachable. Sweep unreachable.
- **Reference Counting**: Count pointers to object. If 0, free. (Fails on cycles).
