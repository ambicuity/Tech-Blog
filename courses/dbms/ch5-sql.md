---
layout: page
title: "DBMS Ch.5: SQL"
permalink: /courses/dbms/ch5-sql/
---

# Chapter 5: SQL: Queries, Constraints, and Triggers

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 5

SQL (Structured Query Language) is the de facto standard for interacting with relational databases.

## 5.1 Basic Structure
The `SFW` block:
```sql
SELECT [DISTINCT] A1, A2, ...
FROM R1, R2, ...
WHERE condition
```

### Conceptual Evaluation Strategy
1.  **FROM**: Compute the Cross Product of tables in `FROM` list.
2.  **WHERE**: Discard tuples that fail the condition.
3.  **SELECT**: Delete unwanted columns.
4.  **DISTINCT**: Eliminate duplicate rows (if specified).

---

## 5.2 Aggregates and Grouping
Aggregate functions (`COUNT`, `SUM`, `AVG`, `MAX`, `MIN`) summarize data.

### GROUP BY and HAVING
```sql
SELECT age, AVG(rating)
FROM Sailors
GROUP BY age
HAVING COUNT(*) > 1;
```
1.  Partition the table into groups based on `age`.
2.  Apply `HAVING` condition to **groups** (discard groups with $\le 1$ sailor).
3.  For each remaining group, generate ONE answer tuple.
    *   *Rule*: You cannot select a column that is not grouped, unless it's in an aggregate. `SELECT name, AVG(rating) GROUP BY age` is ILLEGAL.

---

## 5.3 Nested Queries
A query within a query.

### Uncorrelated Subquery
The inner query runs once.
```sql
SELECT S.sname
FROM Sailors S
WHERE S.sid IN (SELECT R.sid FROM Reserves R WHERE R.bid = 103);
```

### Correlated Subquery
The inner query refers to a value from the outer query. Runs once per row of outer query.
**Query**: Find sailors whose rating is better than the average rating of sailors of the same age.
```sql
SELECT S.sname
FROM Sailors S
WHERE S.rating > (
    SELECT AVG(S2.rating)
    FROM Sailors S2
    WHERE S2.age = S.age  -- Correlation here
);
```

---

## 5.4 Joins in SQL
Since SQL-92, explicit join syntax is preferred over the `WHERE` clause.

*   `INNER JOIN`: Only matching rows.
*   `LEFT OUTER JOIN`: All rows from Left table, plus matches from Right. (NULL if no match).
*   `RIGHT OUTER JOIN`: All rows from Right.
*   `FULL OUTER JOIN`: All rows from Both.

```sql
-- Find all sailors and the boats they reserved (if any)
SELECT S.sname, R.bid
FROM Sailors S
LEFT OUTER JOIN Reserves R ON S.sid = R.sid;
```

---

## 5.5 Integrity Constraints
1.  **Primary Key**: `PRIMARY KEY (sid)`
2.  **Foreign Key**: `FOREIGN KEY (sid) REFERENCES Sailors(sid)`
    *   **On Delete Cascade**: If Sailor deleted, delete their reservations too.
    *   **On Delete Set Null**: If Sailor deleted, set bid to NULL.
3.  **Check**: `CHECK (rating >= 1 AND rating <= 10)`

## 5.6 Triggers
Active Database elements.
```sql
CREATE TRIGGER rating_log
AFTER UPDATE OF rating ON Sailors
FOR EACH ROW
BEGIN
    INSERT INTO LogTable(sid, old_rating, new_rating)
    VALUES (OLD.sid, OLD.rating, NEW.rating);
END;
```
