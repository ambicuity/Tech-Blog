---
layout: page
title: "AI Ch.5: Adversarial Search"
permalink: /courses/ai/ch5-adversarial-search/
---

# Chapter 5: Adversarial Search (Game Theory)

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 5

In domains like Chess, Go, or Tic-Tac-Toe, we are not just searching for a path; we are fighting against an opponent who is actively trying to stop us. This is a **Zero-Sum Game** (if I win +1, you lose -1).

## 5.1 Minimax Algorithm
We assume the opponent (MIN) plays optimally to minimize our score. We (MAX) want to maximize it.

-   **MAX Node**: Value is `max(children)`.
-   **MIN Node**: Value is `min(children)`.
-   **Leaf Node**: Value is utility of state (e.g., +1 for win, -1 for loss).

### Python Implementation

```python
def minimax(state, depth, is_maximizing_player):
    if depth == 0 or game_over(state):
        return evaluate(state)

    if is_maximizing_player:
        max_eval = float('-inf')
        for move in get_moves(state):
            eval = minimax(make_move(state, move), depth - 1, False)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_moves(state):
            eval = minimax(make_move(state, move), depth - 1, True)
            min_eval = min(min_eval, eval)
        return min_eval
```
**Complexity**: Time $O(b^m)$. Space $O(bm)$. (Similar to DFS).
For Chess, $b \approx 35, m \approx 100$. Impossible to solve completely.

---

## 5.2 Alpha-Beta Pruning
We can optimize Minimax without changing the result. Ideally, we want to stop searching a branch if we know it won't be chosen.

-   **Alpha ($\alpha$)**: The value of the best (highest) choice we have found so far at any choice point along the path for MAX.
-   **Beta ($\beta$)**: The value of the best (lowest) choice we have found so far at any choice point along the path for MIN.

### The Pruning Logic
*   **Beta Cutoff**: If we are at a MIN node, and we find a move that has value $v \le \alpha$, we stop. MAX (ancestor) will never choose this path because it already has a better option ($\alpha$).
*   **Alpha Cutoff**: If we are at a MAX node, and we find $v \ge \beta$, we stop. MIN (ancestor) will never choose this path.

### Python Implementation of Alpha-Beta

```python
def alpha_beta(state, depth, alpha, beta, is_maximizing):
    if depth == 0 or game_over(state):
        return evaluate(state)

    if is_maximizing:
        max_eval = float('-inf')
        for move in get_moves(state):
            eval = alpha_beta(make_move(state, move), depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta Cutoff
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_moves(state):
            eval = alpha_beta(make_move(state, move), depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha Cutoff
        return min_eval

# Initial call: alpha_beta(root, depth, -inf, +inf, True)
```

### Effectiveness
With perfect ordering (checking best moves first), time complexity drops to $O(b^{m/2})$.
This effectively doubles the search depth we can reach in the same time.

---

## 5.3 Monte Carlo Tree Search (MCTS)
For games with high branching factors (like Go, $b \approx 250$), Minimax is useless.
MCTS builds a search tree asymmetrically.

1.  **Selection**: Traverse tree to a leaf using "UCB1" policy (balance exploration vs exploitation).
2.  **Expansion**: Add a child node.
3.  **Simulation (Rollout)**: Play random moves from child to end of game.
4.  **Backpropagation**: Update win/loss stats up the tree.

This is the core of **AlphaGo**.
