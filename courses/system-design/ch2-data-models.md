---
layout: page
title: "System Design Ch.2: Data Models"
permalink: /courses/system-design/ch2-data-models/
---

# Chapter 2: Data Models and Query Languages

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 2

Data models are perhaps the most important part of developing software, because they have such a profound effect: not only on how the software is written, but also on how we think about the problem that we are solving.

## 2.1 Relational Model vs. Document Model

### The Relational Model
Proposed by Edgar Codd in 1970. Data is organized into **relations** (tables), where each relation is a collection of **tuples** (rows).
- **Pros**: Good for joins, many-to-many relationships, and rigid schemas.
- **Object-Relational Mismatch**: The disconnect between objects in application code and tables in the DB.

### The Document Model (NoSQL)
Targets use cases where data comes in self-contained documents (JSON, XML).
- **Pros**: Schema flexibility, better locality (all data in one place), closer measurement to application objects.
- **Cons**: Poor support for joins and many-to-many relationships.

> **Conclusion**: If your data has a document-like structure (a tree of one-to-many relationships) where typically the entire tree is loaded at once, then use a document model. If many-to-many relationships are dominant, the relational model is better.

## 2.2 Query Languages for Data
- **Declarative (SQL)**: You tell the computer *what* you want, not *how* to get it. The query optimizer decides the execution path (indexes, join order). Easier to parallelize.
- **Imperative (IMS, CODASYL)**: You tell the computer exactly *how* to traverse the data. Harder to optimize.

### MapReduce Querying
A programming model for processing large datasets with a distributed algorithm on a cluster. It is neither strictly declarative nor imperative but a functional query logic (`map` and `reduce`).

## 2.3 Graph-Like Data Models
When many-to-many relationships are very common, graph models are the natural choice.
- **Property Graphs** (Neo4j): Vertices and edges have properties.
- **Triple Stores** (RDF): Format: `(Subject, Predicate, Object)`.

**Cypher Query Language** (Neo4j):
```cypher
MATCH (person) -[:LOVES]-> (pizza)
RETURN person.name
```
Graph databases are vastly superior to SQL for recursive queries (e.g., "friends of friends of friends").
