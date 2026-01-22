---
layout: page
title: "DBMS Ch.3: Relational Model"
permalink: /courses/dbms/ch3-relational-model/
---

# Chapter 3: The Relational Model

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 3

The **Relational Model** (proposed by Codd in 1970) is the basis for almost all commercial DBMS today (PostgreSQL, MySQL, Oracle).

## 3.1 Concepts
- **Relation**: A set of tuples (rows). Think "Table".
- **Schema**: Specifies name of relation + name and type of each column.
    - `Students(sid: string, name: string, login: string, age: integer, gpa: real)`
- **Instance**: The actual data at a given time.

## 3.2 Integrity Constraints (ICs)
Conditions that must be true for any instance of the database.
1.  **Domain Constraint**: Values in column must be of correct type.
2.  **Primary Key Constraint**: No two distinct tuples can have same key.
3.  **Foreign Key Constraint**: A field in one table refers to a Primary Key in another table.
    - **Referential Integrity**: Unlike pointers in C++, you cannot have a "dangling pointer" in a DB. The DB rejects the delete of the referenced parent (or cascades it).

## 3.3 Translating ER to Relational
- **Entity Set** $\to$ Table.
- **Relationship (Many-to-Many)** $\to$ Table (with Foreign Keys to both entities).
- **Relationship (One-to-Many)** $\to$ Foreign Key in the "Many" side table.
- **Weak Entity** $\to$ Table with Foreign Key to Owner + Owner's PK is part of Weak Entity's PK.
