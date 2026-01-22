---
layout: page
title: "AI Ch.13: Probabilistic Reasoning"
permalink: /courses/ai/ch13-probabilistic-reasoning/
---

# Chapter 13: Probabilistic Reasoning

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 13

The world is uncertain. Logic fails (`Toothache => Cavity` is false).
We use **Probability Theory**.

## 13.1 Bayesian Networks
A directed acyclic graph (DAG) representing conditional dependencies.
- Nodes: Random variables (e.g., `Burglary`, `Alarm`, `Call`).
- Edge $X \to Y$: X directly influences Y.
- **CPT (Conditional Probability Table)**: $P(Y | Parents(Y))$.

## 13.2 Inference
Given Evidence $E=e$ (Alarm rang), what is probability of Query $X$ (Burglary)?
$P(X | E)$.
- **Exact Inference**: Variable Elimination. (NP-hard in general).
- **Approximate Inference**: Monte Carlo (MCMC, Gibbs Sampling).

## 13.3 Conditional Independence
Huge simplification.
If $A \perp B | C$, then $P(A, B | C) = P(A | C) P(B | C)$.
Makes storage linear instead of exponential.
