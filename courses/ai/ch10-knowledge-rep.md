---
layout: page
title: "AI Ch.10: Knowledge Rep"
permalink: /courses/ai/ch10-knowledge-rep/
---

# Chapter 10: Knowledge Representation

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 10

How do we represent complex world concepts in logic?

## 10.1 Ontological Engineering
Organizing concepts into a hierarchy (Taxonomy).
- **Categories**: `Dog`, `Mammal`.
- **Subclass**: `Dog` $\subset$ `Mammal`.
- **Partition**: Disjoint categories (Male/Female).

## 10.2 Events and Mental Objects
- **Situation Calculus**: Describing change over time.
    - `Result(Action, State) -> State`.
- **Frame Problem**: specifying what *doesn't* change. (If I walk, the color of the wall stays same).
- **Mental Events**: `Believes(John, P)`. `Knows(John, P)`.
    - Modal Logic.

## 10.3 Reasoning Systems
- **Semantic Networks**: Graph visualization of logic. Nodes = Objects, Edges = Relations.
- **Description Logics**: Formal subset of FOL used in Semantic Web (OWL).
