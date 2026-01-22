---
layout: page
title: "AI Ch.16: Complex Decisions"
permalink: /courses/ai/ch16-complex-decisions/
---

# Chapter 16: Making Complex Decisions (MDPs)

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 17

Sequential decision problems where the utility depends on a *sequence* of decisions.

## 16.1 Markov Decision Process (MDP)
Defined by:
1.  **S**: States.
2.  **A**: Actions.
3.  **T**: Transition model $P(s' | s, a)$.
4.  **R**: Reward function $R(s)$.

Goal: Find a **Policy** $\pi(s)$ that maps states to actions to maximize discounted cumulative reward.
$$ \text{Utility} = \sum_{t=0}^{\infty} \gamma^t R(s_t) $$
Where $0 \le \gamma < 1$ is the **Discount Factor**.

## 16.2 Bellman Equation
The utility of a state is the immediate reward plus the discounted utility of the next state.
$$ U(s) = R(s) + \gamma \max_{a} \sum_{s'} P(s' | s, a) U(s') $$

## 16.3 Solving MDPs
### Value Iteration
1.  Initialize $U(s) = 0$.
2.  Iterate the Bellman Update rule for all states.
3.  Converges to unique optimal values.

### Policy Iteration
1.  Pick random policy $\pi$.
2.  **Evaluate**: Calculate $U$ for fixed $\pi$ (Linear system of equations).
3.  **Improve**: Update $\pi(s) = argmax_a \sum P(s'|s,a)U(s')$.
4.  Repeat until policy stops changing.
