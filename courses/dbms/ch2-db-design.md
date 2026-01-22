---
layout: page
title: "DBMS Ch.2: DB Design"
permalink: /courses/dbms/ch2-db-design/
---

# Chapter 2: Introduction to Database Design

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 2

Before we even look at tables, we must model the real-world data constraints. We use the **Entity-Relationship (ER) Model**.

## 2.1 The ER Model
- **Entity**: An object in the real world (e.g., `Student`, `Course`).
- **Attributes**: Properties of entities (e.g., `Name`, `GPA`).
- **Entity Set**: Collection of all entities of a type.
- **Relationship**: Association between entities (e.g., `Student` *enrolled in* `Course`).

## 2.2 Key Constraints
- **Primary Key**: Minimal set of fields that uniquely identifies an entity. (Underlined in ER diagrams).
- **Candidate Key**: A key that *could* be primary.

## 2.3 Participation Constraints
- **Total Participation**: Every entity must be involved in the relationship. (Represented by thick line).
    - Example: Every `Department` must have a `Manager`.
- **Partial Participation**: Not every entity is involved.

## 2.4 Weak Entities
An entity that cannot be identified uniquely without an owner entity.
- Example: `Dependent` of an `Employee`. If `Employee` is deleted, `Dependent` vanishes.
- Represented by double rectangle.

## 2.5 Class Hierarchies (ISA)
Inheritance in databases.
- `Employee` ISA `Person`.
- Attributes of `Person` are inherited by `Employee`.
- **Overlap Constraints**: Can a person be both `Student` and `Employee`?
- **Covering Constraints**: Must a person be either `Student` or `Employee`?
