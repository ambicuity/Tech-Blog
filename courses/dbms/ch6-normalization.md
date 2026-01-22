---
layout: page
title: "DBMS Ch.6: Normalization"
permalink: /courses/dbms/ch6-normalization/
---

# Chapter 6: Schema Refinement and Normalization

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 19 (Mapped to Ch 6 in generic syllabus)

Bad DB design leads to **Redundancy** and **Anomalies**. Normalization is the cure.

## 6.1 Problems with Redundancy
Table `Hourly_Emps(ssn, name, lot, rating, hourly_wages, hours_worked)`.
If rating determines wages, we repeat logical data for every employee with same rating.
*   **Update Anomaly**: Changing wage for rating 8 requires updating all rows.
*   **Insertion Anomaly**: Cannot store wage for rating 8 if no employee has it.
*   **Deletion Anomaly**: Deleting last employee with rating 8 loses the wage info.

## 6.2 Functional Dependencies (FDs)
$X \to Y$: If two tuples agree on attributes $X$, they must agree on $Y$.
*   `rating -> hourly_wages`
*   `ssn -> name, lot, rating, ...`

## 6.3 Normal Forms
Decompose relations to eliminate redundancy.
*   **1NF**: Atomic values.
*   **2NF**: No partial dependency (non-key attribute depends on part of composite key).
*   **3NF**: No transitive dependency ($X \to Y \to Z$).
    *   Def: For every FD $X \to A$, either $X$ is a superkey OR $A$ is part of a key.
*   **BCNF (Boyce-Codd Normal Form)**: Stricter.
    *   Def: For every FD $X \to A$, $X$ MUST be a superkey.

## 6.4 Decomposition
We split table $R$ into $R_1, R_2$.
*   **Lossless Join Property**: Essential. $R_1 \bowtie R_2$ must equal original $R$.
*   **Dependency Preservation**: Desirable. All FDs can be checked within single tables.
*   BCNF is always lossless but may not preserve dependencies. verify 3NF preserves both.
