---
layout: page
title: "OS Ch.11: File-System Interface"
permalink: /courses/os/ch11-fs-interface/
---

# Chapter 11: File-System Interface

> **Reference**: *Operating System Concepts* by Silberschatz et al., Chapter 11

The file system limits the user's view of storage to a logical unit called a **File**.

## 11.1 File Concept
A named collection of related information recorded on secondary storage.
- **Attributes**: Name, Identifier, Type, Location, Size, Protection, Timestamps.
- **Operations**: Create, Write, Read, Reposition (Seek), Delete, Truncate.

## 11.2 Access Methods
- **Sequential Access**: Read next, Write next. (Tapes, most files).
- **Direct Access**: Read block $n$. (Databases).

## 11.3 Directory Structure
The directory records information about files.
- **Single-Level**: One dir for all users. Naming collision nightmare.
- **Two-Level**: User File Directory (UFD) per user.
- **Tree-Structured**: Arbitrary depth. Subdirectories. (Standard today).
- **Acyclic-Graph**: Allows shared subdirectories (Links/Aliases).
    - Hard Link: Another pointer to the index node (inode).
    - Symbolic Link: A file that contains the path to another.

## 11.4 Protection
- **Types of Access**: Read, Write, Execute, Append, Delete, List.
- **Access Control List (ACL)**: List of `(User, Access)` for every file. Flexible but tedious.
- **Owner/Group/World (Unix)**:
    - 3 classes: Owner, Group, Universe.
    - 3 bits: RWX. (e.g., `rwxr-x---` = 750).
