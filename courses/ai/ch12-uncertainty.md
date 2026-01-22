---
layout: page
title: "AI Ch.12: Uncertainty"
permalink: /courses/ai/ch12-uncertainty/
---

# Chapter 12: Quantifying Uncertainty

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 12

Logic is brittle. Probability is robust.

## 12.1 Basics of Probability
- **Prior Probability**: $P(Cavity) = 0.1$.
- **Posterior Probability**: $P(Cavity | Toothache)$.
- **Random Variables**: Boolean (`Cavity`), Discrete (`Weather`), Continuous (`Temp`).
- **Joint Distribution**: $P(A, B, C)$. Table of size $2^N$. Contains *all* info.

## 12.2 Baye's Rule
The fundamental law of AI.
$$ P(A | B) = \frac{P(B | A) P(A)}{P(B)} $$
- Allows diagnosis. We know $P(Symptom | Disease)$ (Causal). We want $P(Disease | Symptom)$ (Diagnostic).

## 12.3 Independence
- $A$ is independent of $B$ if $P(A | B) = P(A)$.
- Critical for reducing complexity.
- **Naive Bayes Classifier**: Assume all effects are independent given cause.
    - $P(Cause | E_1, \dots E_n) \propto P(Cause) \prod P(E_i | Cause)$.
    - Used in Spam filters.
