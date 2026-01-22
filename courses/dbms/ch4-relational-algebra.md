---
layout: page
title: "DBMS Ch.4: Relational Algebra"
permalink: /courses/dbms/ch4-relational-algebra/
---

# Chapter 4: Relational Algebra and Calculus

> **Reference**: *Database Management Systems* by Ramakrishnan & Gehrke, Chapter 4

Relational Algebra is the mathematical foundation of modern databases. It is a procedural language that describes *how* to compute a result. Understanding it is crucial for understanding Query Optimization.

## 4.1 Fundamental Operators

The five basic operators in Relational Algebra are:

### 1. Selection ($\sigma$)
Selects a subset of rows from a relation that satisfy a condition.
$$ \sigma_{p}(R) = \{ t \mid t \in R \land p(t) \} $$
*   **Example**: Find students older than 20.
    *   $\sigma_{age > 20}(Students)$

### 2. Projection ($\pi$)
Selects a subset of columns. Result contains distinct tuples (duplicates are eliminated in pure algebra, though SQL keeps them usually).
$$ \pi_{L}(R) $$
*   **Example**: Return names and ratings.
    *   $\pi_{name, rating}(Students)$

### 3. Cross Product ($\times$)
Combines two relations. Each row of $R$ is paired with each row of $S$.
$$ R \times S $$
*   If $R$ has $N$ rows and $M$ columns, and $S$ has $K$ rows and $L$ columns, result has $N \cdot K$ rows and $M + L$ columns.

### 4. Set Difference ($-$)
Tuples in $R$ but not in $S$. $R$ and $S$ must be **Union-Compatible** (same schema).
$$ R - S $$

### 5. Union ($\cup$)
Tuples in $R$ or $S$.
$$ R \cup S $$

---

## 4.2 Derived Operators

### 1. Join ($\bowtie$)
The most common operator. It is essentially a Cross Product followed by a Selection.
$$ R \bowtie_{c} S = \sigma_{c}(R \times S) $$

*   **Natural Join** ($R \bowtie S$): Joins on all attributes with the same name.
*   **Equi-Join**: Condition $c$ contains only equalities ($=$).

### 2. Intersection ($\cap$)
$$ R \cap S = R - (R - S) $$

### 3. Division ($/$)
Used for queries like "Find students who have taken ALL courses required for CS".
$$ R / S = \{ t \mid \forall s \in S, \langle t, s \rangle \in R \} $$

**Example**:
*   $R(x, y)$ has (A, 1), (A, 2), (B, 1).
*   $S(y)$ has (1), (2).
*   $R / S$ = (A). (Since A is paired with both 1 and 2).

---

## 4.3 Examples of Complex Queries

**Schema**:
*   `Sailors(sid, sname, rating, age)`
*   `Boats(bid, bname, color)`
*   `Reserves(sid, bid, day)`

**Query 1**: Find names of sailors who have reserved boat 103.
1.  Compute $\sigma_{bid=103}(Reserves)$.
2.  Join with Sailors: $Sailors \bowtie (\sigma_{bid=103}(Reserves))$.
3.  Project Name: $\pi_{sname}(Sailors \bowtie \sigma_{bid=103}(Reserves))$.

**Query 2**: Find names of sailors who have reserved a 'Red' boat.
$$ \pi_{sname}( ( \sigma_{color='Red'}(Boats) ) \bowtie Reserves \bowtie Sailors ) $$

---

## 4.4 Tuple Relational Calculus (TRC) implies SQL
TRC is a **declarative** query language (Non-procedural). It describes *what* you want.
$$ \{ t \mid P(t) \} $$
*   $\{ S \mid S \in Sailors \land S.rating > 7 \}$

SQL is largely based on TRC, but the query optimizer translates it into Relational Algebra plans for execution.
