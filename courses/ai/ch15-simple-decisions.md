---
layout: page
title: "AI Ch.15: Simple Decisions"
permalink: /courses/ai/ch15-simple-decisions/
---

# Chapter 15: Making Simple Decisions (Utility Theory)

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 16

In Ch 7 (Logic), agents had goals. In Ch 12 (Probability), agents had beliefs.
Now, agents have **Preferences**.
**Decision Theory = Probability Theory + Utility Theory**.

## 15.1 Basics of Utility
-   **Utility Function $U(S)$**: Maps a state to a real number describing "how happy" the agent is.
-   **Maximum Expected Utility (MEU)**: Rational agents choose the action that maximizes expected utility.
    $$ action = \text{argmax}_a \sum_{s'} P(Result(a) = s') U(s') $$

## 15.2 Utility Axioms
To be rational, preferences must obey logic:
1.  **Orderability**: $(A \succ B) \lor (B \succ A) \lor (A \sim B)$.
2.  **Transitivity**: $(A \succ B) \land (B \succ C) \implies (A \succ C)$.
3.  **Continuity**, **Substitutability**, **Monotonicity**.

If you violate these, you can be "money-pumped" (tricked into losing money indefinitely).

## 15.3 Value of Information
Is it worth paying to acquire evidence $E_j$?
$$ VPI(E_j) = (\text{Exp. Utility given } E_j) - (\text{Current Exp. Utility}) $$
*   VPI is always non-negative. Information never hurts (on average).
