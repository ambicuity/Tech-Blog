---
layout: page
title: "DBMS Ch.4: Relational Algebra"
permalink: /courses/dbms/ch4-relational-algebra/
---

# Chapter 4: Relational Algebra

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 4

Relational Algebra is a theoretical procedural query language. It precisely defines the operations that you can perform on data. SQL is practically "syntactic sugar" for Relational Algebra.

## 4.1 Basic Operators
1.  **Selection ($\sigma$)**: Choose rows. `sigma_{age > 18}(Students)`.
2.  **Projection ($\pi$)**: Choose columns. `pi_{name, gpa}(Students)`.
3.  **Cross Product ($\times$)**: Combine two tables. Every row of A paired with every row of B.
4.  **Set Difference ($-$)**: Tuples in A but not in B.
5.  **Union ($\cup$)**: Tuples in A or B.

## 4.2 Derived Operators
1.  **Join ($\bowtie$)**: Cross Product followed by Selection.
    - `Students bowtie Enrolled` matches Student.Sid with Enrolled.Sid.
2.  **Intersection ($\cap$)**: $A \cap B = A - (A - B)$.
3.  **Division (/)**: Used for "For All" queries. Find students who have taken *all* courses.

## 4.3 Query Optimization
- The Algebraic operators allow the DBMS to rewrite queries.
- $\sigma_{c1}(\sigma_{c2}(R)) \equiv \sigma_{c1 \land c2}(R)$.
- $\sigma_{c}(R \bowtie S) \equiv (\sigma_c(R)) \bowtie S$ (Pushing selection down is huge for performance).
