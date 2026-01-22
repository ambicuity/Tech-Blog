---
layout: page
title: "DBMS Ch.7: App Development"
permalink: /courses/dbms/ch7-app-development/
---

# Chapter 7: Database Application Development

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 6

SQL is not enough. Real apps need a host language (Java, Python, C++).

## 7.1 Embedded SQL
Embedding SQL directly in C code.
`EXEC SQL SELECT ...`. Preprocessor replaces it with API calls.
*   **Cursors**: Used to iterate over result sets (Impedance Mismatch between Set-oriented SQL and Record-oriented C).

## 7.2 API Standards (ODBC and JDBC)
Driver-based architecture. Application is independent of DBMS.
**JDBC Steps**:
1.  Load Driver (`Class.forName()`).
2.  Connect (`DriverManager.getConnection(url)`).
3.  Statement (`conn.createStatement()`).
4.  ResultSet (`stmt.executeQuery()`).
5.  Iterate (`rs.next()`).

## 7.3 Stored Procedures
Logic stored inside the DBMS (PL/SQL).
*   **Pros**: Close to data (fast), Security (APIs), Shared logic.
*   **Cons**: Vendor lock-in, harder to debug.

## 7.4 Object-Relational Mapping (ORM)
Hibernate, JPA, Django ORM.
*   Maps Java Objects ("Beans") to Tables.
*   Automates SQL generation.
*   **N+1 Problem**: Loading a list of Parents and then fetching Children for each one = N+1 queries. Solve with `JOIN FETCH`.
