---
layout: page
title: "AI Ch.13: Probabilistic Reasoning"
permalink: /courses/ai/ch13-probabilistic-reasoning/
---

# Chapter 13: Probabilistic Reasoning (Bayesian Networks)

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 13

Knowledge Representation using Logic (Ch 7) assumes certainty. Real world is uncertain.

## 13.1 Bayesian Networks
A directed acyclic graph (DAG) where:
-   **Nodes**: Random variables ($X_i$).
-   **Edges**: Direct influence.
-   **CPT**: Each node $X_i$ has a conditional probability distribution $P(X_i | Parents(X_i))$.

### Semantics
The network defines the **Full Joint Distribution**:
$$ P(x_1, \dots, x_n) = \prod_{i=1}^n P(x_i | Parents(x_i)) $$
*   *Example*: Burglary Network.
    *   $P(B, E, A, J, M) = P(B) P(E) P(A|B,E) P(J|A) P(M|A)$.
    *   This reduces parameters from $2^5 - 1 = 31$ to $1 + 1 + 4 + 2 + 2 = 10$. Massive savings!

---

## 13.2 Exact Inference
Goal: Compute $P(Query | Evidence)$.

### Enumeration
Summing terms from the full joint distribution.
$P(B | j, m) = \alpha \sum_e \sum_a P(B) P(e) P(a|B,e) P(j|a) P(m|a)$.
*   Cost: $O(2^n)$.

### Variable Elimination
Optimizes enumeration by moving summations inwards.
$$ \sum_e P(e) \sum_a P(a|B,e) \dots $$
*   Factors: Intermedate tables.
*   Operation: Pointwise product and summing out variables.
*   Complexity: exponential in the tree-width of the network.

---

## 13.3 Approximate Inference
For large networks, exact inference is intractable.
**Monte Carlo Sampling**:
1.  **Direct Sampling**: Generate samples from joint distribution. Count matches.
2.  **Rejection Sampling**: Reject samples contradicting evidence.
3.  **Gibbs Sampling (MCMC)**: Markov Chain Monte Carlo.
    *   Start with random assignment.
    *   Iteratively resample one variable $X_i$ given its **Markov Blanket** (Parents, Children, Children's Parents).
    *   Converges to true posterior.
