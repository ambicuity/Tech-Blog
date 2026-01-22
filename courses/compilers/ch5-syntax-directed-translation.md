---
layout: page
title: "Compilers Ch.5: Translation"
permalink: /courses/compilers/ch5-syntax-directed-translation/
---

# Chapter 5: Syntax-Directed Translation

> **Reference**: *Compilers* (Dragon Book), Chapter 5

How do we associate meaning (semantics) with the syntax tree? We use **Attributes** and **Semantic Rules**.

## 5.1 Attributes
- **Synthesized Attributes**: Computed from children nodes. (e.g., `E.val = E1.val + T.val`). Values flow **up** the tree.
- **Inherited Attributes**: Computed from parent or siblings. (e.g., Type declaration passed down to variables). Values flow **down** or **sideways**.

## 5.2 Dependency Graphs
Shows order of evaluation. If there are no cycles, we can evaluate attributes in a **Topological Sort** order.

## 5.3 L-Attributed Definitions
A class of definitions where attributes can be evaluated in a single Left-to-Right pass (compatible with LL parsers).
- Synthesized attributes allowed anywhere.
- Inherited attributes can only depend on values to the left.
