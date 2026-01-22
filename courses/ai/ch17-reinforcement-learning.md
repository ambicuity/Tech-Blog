---
layout: page
title: "AI Ch.17: Reinforcement Learning"
permalink: /courses/ai/ch17-reinforcement-learning/
---

# Chapter 17: Reinforcement Learning (RL)

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 21/22

MDPs assume we know the transition model $P(s'|s,a)$ and rewards $R(s)$.
**Reinforcement Learning** is solving MDPs *without* knowing T or R. We must explore the world.

## 17.1 Passive RL
Evaluate a fixed policy $\pi$.
-   **Direct Utility Estimation**: Run many trials. Average the reward-to-go for each state.
-   **Adaptive Dynamic Programming (ADP)**: Learn model $P$ and $R$ from history, then solve MDP. (Model-Based).
-   **Temporal Difference (TD) Learning**: Update utility based on difference between predicted and actual next state. (Model-Free).
    $$ U(s) \leftarrow U(s) + \alpha (R(s) + \gamma U(s') - U(s)) $$

## 17.2 Active RL (Q-Learning)
Learn the optimal policy. We learn **Q-Values** $Q(s, a)$ (Quality of action $a$ in state $s$).
$$ Q(s, a) \leftarrow Q(s, a) + \alpha (R(s) + \gamma \max_{a'} Q(s', a') - Q(s, a)) $$
-   **Off-Policy**: Learns optimal policy even while acting randomly.

## 17.3 Exploration vs Exploitation
-   **$\epsilon$-Greedy**: With probability $\epsilon$, pick random action. Else pick $argmax_a Q(s, a)$.
-   **Upper Confidence Bound (UCB)**: Boost actions we haven't tried much.
