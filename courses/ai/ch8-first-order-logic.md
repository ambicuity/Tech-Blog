---
layout: page
title: "AI Ch.8: First-Order Logic"
permalink: /courses/ai/ch8-first-order-logic/
---

# Chapter 8: First-Order Logic

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 8

Propositional logic ($A \land B$) is too simple. It cannot express "All men are mortal" easily (requries infinite list for every man).
**First-Order Logic (FOL)** is more expressive.

## 8.1 Syntax and Semantics
- **Constants**: `John`, `Crown`.
- **Predicates**: `Brother(Richard, John)`, `King(John)`.
- **Functions**: `LeftLeg(John)` (returns an object).
- **Quantifiers**:
    - $\forall$ (Universal): "For all". $\forall x, King(x) \Rightarrow Person(x)$.
    - $\exists$ (Existential): "There exists". $\exists x, Crown(x) \land OnHead(x, John)$.

## 8.2 Using FOL
- **Axioms**: Basic facts.
- **Definitions**: $\forall a, b,  Brother(a, b) \iff Sibling(a, b) \land Male(a)$.
- **Domain**: The set of objects in the world.

## 8.3 Engineering a Knowledge Base
1.  Identify the task.
2.  Assemble relevant knowledge.
3.  Decide on a vocabulary (Predicates/Functions).
4.  Encode general knowledge (Axioms).
5.  Encode specific problem instance.
6.  Query the inference procedure.
