---
layout: page
title: "AI Ch.6: CSPs"
permalink: /courses/ai/ch6-constraint-satisfaction/
---

# Chapter 6: Constraint Satisfaction Problems (CSPs)

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 6

In standard search, state is a "black box". In CSPs, state is defined by **Variables** $X_i$ with values from domain $D_i$.
Goal: Assign values to all variables satisfying **Constraints**.

## 6.1 Examples
- **Map Coloring**: Variables = Regions. Domain = {Red, Green, Blue}. Constraint = Neighbors cannot have same color.
- **Sudoku**: Variables = Cells. Domain = 1..9. Constraints = Rows/Cols/Boxes unique.

## 6.2 Backtracking Search
DFS for CSPs.
- Select unassigned variable.
- Try value.
- Check consistency.
- Recurse.

## 6.3 Improving Backtracking
1.  **MRV (Minimum Remaining Values)**: Pick variable with fewest legal values left ("Fail First").
2.  **Least Constraining Value**: Pick value that rules out fewest choices for neighbors.
3.  **Forward Checking**: Keep track of remaining legal values for unassigned variables. If any domain becomes empty, backtrack immediately.
4.  **AC-3 (Arc Consistency)**: Propagate constraints deeper than forward checking.
