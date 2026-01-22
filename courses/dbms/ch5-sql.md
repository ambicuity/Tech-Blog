---
layout: page
title: "DBMS Ch.5: SQL"
permalink: /courses/dbms/ch5-sql/
---

# Chapter 5: SQL: Queries, Programming, Triggers

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 5

Structured Query Language (SQL) is the standard commercial language for RDBMS.

## 5.1 Basic Queries
The SFW block:
```sql
SELECT DISTINCT target-list
FROM relation-list
WHERE qualification
```
- Semantics:
    1.  Compute Cross Product of relations in `FROM`.
    2.  Filter rows satisfying `WHERE`.
    3.  Output columns in `SELECT`.

## 5.2 Aggregates and Grouping
- `COUNT`, `SUM`, `AVG`, `MAX`, `MIN`.
- `GROUP BY`: Partition rows into groups. Aggregate is applied per group.
- `HAVING`: Filter groups *after* aggregation.
```sql
SELECT age, AVG(gpa)
FROM Students
GROUP BY age
HAVING COUNT(*) > 5
```

## 5.3 Nested Queries
A query within a query.
- `IN`, `EXISTS`, `ANY`, `ALL`.
- **Correlated Nested Query**: Inner query refers to a value from the outer query (Loop semantics).

## 5.4 Triggers
Event-Condition-Action.
- Automatic side-effect when database is modified.
- `CREATE TRIGGER young_student_check BEFORE INSERT ON Students ...`
