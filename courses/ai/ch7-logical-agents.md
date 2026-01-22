---
layout: page
title: "AI Ch.7: Logical Agents"
permalink: /courses/ai/ch7-logical-agents/
---

# Chapter 7: Logical Agents

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 7

Humans use **Knowledge** to reason.
**Knowledge-Based Agents**:
- Maintain a **Knowledge Base (KB)** (Set of sentences).
- **TELL**: Add new sentence.
- **ASK**: Query what is known.

## 7.1 Wumpus World
A grid cave with pits, a Wumpus monster, and gold.
- Agent perceives: Stench (near Wumpus), Breeze (near Pit), Glitter (Gold).
- Needs logic to deduce safety. "If Breeze in (1,1), then Pit in (1,2) or (2,1)".

## 7.2 Propositional Logic
- **Symbols**: $P, Q, R$.
- **Connectives**: $\neg$ (Not), $\land$ (And), $\lor$ (Or), $\Rightarrow$ (Implies), $\iff$ (Biconditional).
- **Entailment** ($KB \models \alpha$): In every model where KB is true, $\alpha$ is also true.

## 7.3 Theorem Proving
- **Model Checking**: Enumerate all truth tables (Exponential).
- **Inference Rules**:
    - **Modus Ponens**: $\alpha \Rightarrow \beta, \alpha \vdash \beta$.
    - **Resolution**: $(\alpha \lor \beta) \land (\neg \beta \lor \gamma) \vdash (\alpha \lor \gamma)$.
    - Completeness: Resolution is complete for Propositional Logic.
