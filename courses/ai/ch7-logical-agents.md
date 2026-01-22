---
layout: page
title: "AI Ch.7: Logical Agents"
permalink: /courses/ai/ch7-logical-agents/
---

# Chapter 7: Logical Agents

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 7

Knowledge-based agents operate by storing sentences about the world in a **Knowledge Base (KB)** and using an **Inference Engine** to deduce new facts.

## 7.1 Wumpus World
A testbed for logic agents.
-   **Grid**: 4x4.
-   **Hazards**: Pits (Breeze), Wumpus (Stench).
-   **Goal**: Find Gold (Glitter).
-   **Rules**:
    -   $B_{i,j} \iff (P_{i+1, j} \lor P_{i-1, j} \lor P_{i, j+1} \lor P_{i, j-1})$
    -   "A Breeze is present if and only if a Pit is adjacent."

---

## 7.2 Propositional Logic Syntax
*   **Atomic Sentences**: Single symbols ($P, Q$).
*   **Complex Sentences**: Built with connectives ($\neg, \land, \lor, \Rightarrow, \iff$).

### Semantics
A **Model** assigns True/False to every symbol.
*   **Entailment ($KB \models \alpha$)**: $\alpha$ is true in *every* model where $KB$ is true.
*   **Validity**: A sentence is valid (Tautology) if it is true in all models. ($P \lor \neg P$).
*   **Satisfiability**: A sentence is satisfiable if it is true in *some* model.

---

## 7.3 Inference Algorithms

### 1. Model Checking
Enumerate all $2^n$ possible models (truth tables). Check if KB is true $\implies \alpha$ is true.
**Complexity**: Exponential.

### 2. Resolution (Proof by Contradiction)
To prove $KB \models \alpha$, we check if $(KB \land \neg \alpha)$ is UNSATISFIABLE.
**CNF (Conjunctive Normal Form)**: A conjunction of clauses. Each clause is a disjunction of literals.
$(A \lor \neg B) \land (B \lor C \lor \neg D)$.

**The Resolution Rule**:
$$ \frac{l_1 \lor \dots \lor l_k, \quad m_1 \lor \dots \lor m_n}{l_1 \lor \dots \lor l_{i-1} \lor l_{i+1} \dots \lor m_1 \dots m_{j-1} \lor m_{j+1} \dots} $$
where $l_i$ and $m_j$ are complementary ($\neg P$ and $P$).

### 3. DPLL Algorithm
An optimized backtracking search for satisfiability (SAT Solvers).
Used recursively.
1.  **Early Termination**: If a clause is false, return False. If all true, return True.
2.  **Pure Symbol Heuristic**: If a symbol appears with the same sign in all clauses, assign it that value.
3.  **Unit Clause Heuristic**: If a clause has only 1 literal (or 1 unassigned literal), assign it.

### 4. WalkSAT (Local Search)
Randomized hill-climbing.
*   Pick an unsatisfied clause.
*   Flip the value of a variable in that clause.
*   Repeat Max_Flips times.
*   Often extremely fast, but incomplete.
