---
layout: page
title: "AI Ch.14: HMMs"
permalink: /courses/ai/ch14-hmms/
---

# Chapter 14: Probabilistic Reasoning over Time

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 14

Reasoning about states that change (Temporal Models).
Input: Sequence of observations. Output: State sequence.

## 14.1 Markov Models
- **Markov Assumption**: Current state depends only on finite history (usually just previous state).
- $P(X_t | X_{0:t-1}) = P(X_t | X_{t-1})$.

## 14.2 Hidden Markov Models (HMM)
The state $X_t$ is hidden (not visible). We see observation $E_t$.
- **Transition Model**: $P(X_t | X_{t-1})$.
- **Sensor Model**: $P(E_t | X_t)$.

## 14.3 Inference Tasks
1.  **Filtering**: Compute current belief state given all evidence to date. $P(X_t | e_{1:t})$. (Where am I now?).
2.  **Prediction**: Future state. $P(X_{t+k} | e_{1:t})$.
3.  **Smoothing**: Past state. $P(X_k | e_{1:t})$ where $k < t$. (What happened back then?).
4.  **Most Likely Explanation**: $argmax P(x_{1:t} | e_{1:t})$. (Viterbi Algorithm).

## 14.4 Kalman Filters
HMM with continuous variables (Gaussian distribution). Used in guidance/navigation.
