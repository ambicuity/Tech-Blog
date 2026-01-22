---
layout: page
title: "AI Ch.9: Inference in FOL"
permalink: /courses/ai/ch9-inference-in-fol/
---

# Chapter 9: Inference in First-Order Logic

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 9

We saw syntax in Ch.8. Now, how do we reason?
Propositional inference is easy but inefficient for FOL. We need **Unification** and **Generalized Modus Ponens**.

## 9.1 Unification
To apply a rule like $\forall x, King(x) \land Greedy(x) \Rightarrow Evil(x)$, we must match it to facts `King(John)` and `Greedy(John)`.
**Unify**($\alpha, \beta$) returns a substitution $\theta$ such that $\alpha\theta = \beta\theta$.

*   Unify(`Knows(John, x)`, `Knows(John, Jane)`) $\to \{x/Jane\}$.
*   Unify(`Knows(John, x)`, `Knows(y, Bill)`) $\to \{x/Bill, y/John\}$.

## 9.2 Generalized Modus Ponens (GMP)
If we have a rule $p_1 \land p_2 \dots \Rightarrow q$ and facts $p_1', p_2' \dots$ that unify with $p_i$, we can infer $q\theta$.
This is the basis of **Forward Chaining** in production systems.

## 9.3 Forward and Backward Chaining
*   **Forward Chaining**: Data-driven. Start with facts. Apply rules to generate new facts. (Used in Deductive Databases).
*   **Backward Chaining**: Goal-directed. Start with query `Evil(x)?`. Look for rules that imply `Evil`. Prove premises. (Used in Prolog).

## 9.4 Resolution in FOL
Generalized Resolution Rule.
1.  Convert to CNF (Skolemization implies removing existential quantifiers).
2.  Resolve two clauses if they contain complementary literals that unify.
3.  Apply until Empty Clause (Contradiction).
