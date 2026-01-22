---
layout: page
title: "AI Ch.6: Constraint Satisfaction"
permalink: /courses/ai/ch6-constraint-satisfaction/
---

# Chapter 6: Constraint Satisfaction Problems (CSPs)

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 6

In standard search (Ch 3), the state is a "black box". In CSPs, the state is factored into **Variables** with **Values** from **Domains**.
A solution is an assignment that satisfies all **Constraints**.

## 6.1 Formal Definition
A CSP is a triple $(X, D, C)$:
1.  **X**: Set of variables $\{X_1, \dots, X_n\}$.
2.  **D**: Set of domains $\{D_1, \dots, D_n\}$.
3.  **C**: Set of constraints specifying allowable combinations of values.

### Example: Map Coloring
-   **Variables**: $WA, NT, Q, NSW, V, SA, T$ (Regions of Australia).
-   **Domain**: $\{Red, Green, Blue\}$.
-   **Constraints**: Neighboring regions must have different colors. (e.g., $WA \neq NT$).

---

## 6.2 Backtracking Search
The standard algorithm for CSPs. It is a Depth-First Search that assigns one variable at a time.

```python
def backtracking_search(csp):
    return recursive_backtracking({}, csp)

def recursive_backtracking(assignment, csp):
    if len(assignment) == len(csp.variables):
        return assignment  # Complete!
    
    # 1. Select Unassigned Variable
    var = select_unassigned_variable(assignment, csp)
    
    # 2. Order Domain Values
    for value in order_domain_values(var, assignment, csp):
        if is_consistent(var, value, assignment, csp):
            assignment[var] = value
            
            # 3. Inference (Optional but recommended)
            if inference(csp, var, value):
                result = recursive_backtracking(assignment, csp)
                if result: 
                    return result
            
            del assignment[var]  # Backtrack
            
    return None  # Failure
```

## 6.3 Improving Efficiency

### 1. Variable Selection Heuristics
*   **Minimum Remaining Values (MRV)**: Choose the variable with the *fewest* legal values left. "Fail first" principle.
*   **Degree Heuristic**: Choose variable involved in largest number of constraints.

### 2. Value Ordering Heuristics
*   **Least Constraining Value (LCV)**: Choose the value that rules out the *fewest* values in the remaining variables. "Leave maximum flexibility".

### 3. Inference (Pruning)
*   **Forward Checking**: Whenever variable $X$ is assigned, look at connected unassigned neighbor $Y$. Remove inconsistent values from $Y$'s domain. If $Y$ becomes empty, backtrack immediately.
*   **AC-3 (Arc Consistency)**: Stronger than Forward Checking. Propagates constraints through the entire graph.
    *   Arc $X_i \to X_j$ is consistent if for every value $x \in D_i$, there is some value $y \in D_j$ that satisfies the constraint.

---

## 6.4 The structure of Problems
*   **Tree-Structured CSPs**: Can be solved in linear time $O(n d^2)$ using topological sort.
*   **Cutset Conditioning**: Remove a subset of variables (Cutset) to turn the graph into a tree.
