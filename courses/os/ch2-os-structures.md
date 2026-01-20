---
layout: page
title: "OS Ch.2: OS Structures"
permalink: /courses/os/ch2-os-structures/
---

# Chapter 2: Operating-System Structures

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 2

This chapter describes the services an operating system provides to users, processes, and other systems.

## 2.1 Operating-System Services
The OS provides an environment for the execution of programs.
1.  **User Interface**: CLI (Command Line), GUI (Graphical), Touch.
2.  **Program Execution**: Load a program into memory and run it.
3.  **I/O Operations**: A running program may require I/O (file or device).
4.  **File-system Manipulation**: Read, write, create, delete files.
5.  **Communications**: Processes exchanging information (Shared Memory or Message Passing).
6.  **Error Detection**: CPU, memory, or I/O errors.

## 2.2 System Calls
System calls provide an interface to the services made available by the OS. They are typically written in C or C++.
- **API**: Most developers program against an Application Programming Interface (API) like Win32 or POSIX, rather than direct system calls.
- **Execution**: The system-call interface intercepts function calls in the API and invokes the necessary system call within the kernel.

**Types of System Calls**:
- Process Control (`fork`, `exit`, `wait`)
- File Management (`open`, `read`, `write`)
- Device Management (`ioctl`)
- Information Maintenance (`get_time`)
- Communications (`pipe`, `shm_open`)

## 2.3 Linkers and Loaders
- **Source Code** $\to$ **Compiler** $\to$ **Object Code**.
- **Linker**: Combines into a single binary executable file. Links libraries.
- **Loader**: Loads the binary executable into memory to create a **Process**.

## 2.4 Operating-System Structure
How is the kernel organized?

### 1. Monolithic Structure (e.g., Linux, UNIX)
- The entire OS is placed in the kernel space.
- **Pros**: distinct performance advantage (little overhead in system calls).
- **Cons**: Difficult to implement and maintain. One bug can crash the whole system.

### 2. Layered Approach
- OS is divided into layers (Layer 0 is hardware, Layer N is UI).
- Easier to debug, but performance overhead due to traversal of layers.

### 3. Microkernels (e.g., Mach, QNX)
- Moves as much from the kernel into "user space" as possible.
- **Pros**: Easier to extend, more secure/reliable (service crash doesn't crash kernel).
- **Cons**: Performance overhead of excessive message passing.

### 4. Modules (e.g., Solaris, Modern Linux)
- Loadable Kernel Modules (LKM). Data structures and drivers are loaded dynamically.
- Hybrid approach: Monolithic efficiency + Modular flexibility.
