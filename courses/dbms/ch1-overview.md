---
layout: page
title: "DBMS Ch.1: Overview"
permalink: /courses/dbms/ch1-overview/
---

# Chapter 1: Overview of Database Systems

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 1

A **Database Management System (DBMS)** is software designed to assist in maintaining and utilizing large collections of data.

## 1.1 Why use a DBMS?
Why not just store data in text files?
1.  **Data Independence**: Application code should not break if storage format changes.
2.  **Efficient Data Access**: Indexes allow fast lookup without scanning entire files.
3.  **Data Integrity/Security**: Enforce constraints (age > 0) and Access Control.
4.  **Concurrent Access**: Allow 1000 users to edit data simultaneously safely.
5.  **Crash Recovery**: Protect data from system failures (ACID).

## 1.2 Data Models
A data model is a collection of high-level data description constructs.
- **Relational Model**: The dominant model. Data is stored in **Tables** (Relations).
    - **Schema**: Description of data (Columns, Types).
    - **Instance**: The actual data (Rows).
- **Semistructured Model**: XML, JSON.
- **Key-Value**: No schema.

## 1.3 Levels of Abstraction
1.  **External Actions (Views)**: What a specific user group sees (e.g., Student sees Grades, Admin sees Salary).
2.  **Conceptual Schema**: Describes *all* data entity types and relationships.
3.  **Physical Schema**: How data is actually stored on disk (Byte offsets, Indexes).

## 1.4 Database Acting People
- **Database Administrator (DBA)**: Designs Schema, Security, Performance tuning.
- **Application Developers**: Write SQL/Transactions.
- **End Users**: Use the application.
