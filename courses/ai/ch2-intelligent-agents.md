---
layout: page
title: "AI Ch.2: Intelligent Agents"
permalink: /courses/ai/ch2-intelligent-agents/
---

# Chapter 2: Intelligent Agents

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 2

An **agent** perceives its **environment** through **sensors** and acts upon it through **actuators**.

## 2.1 Rationality
A rational agent selects an action that is expected to maximize its performance measure, given the evidence provided by the percept sequence.

## 2.2 PEAS Description
To design an agent, we must specify:
1.  **P**erformance Measure: What defines success? (e.g., Safe, Fast, Legal).
2.  **E**nvironment: Where does it operate? (e.g., Roads, Traffic).
3.  **A**ctuators: How does it move? (e.g., Steering, Brake).
4.  **S**ensors: How does it see? (e.g., Camera, LIDAR).

## 2.3 Environment Types
- **Fully Observable vs. Partially Observable**: Can I see everything? (Chess: Yes. Poker: No).
- **Deterministic vs. Stochastic**: Does next state depend only on current state + action? (Solitaire: Yes. Driving: No).
- **Episodic vs. Sequential**: Does current decision affect future decisions? (Image Classification: Episodic. Chess: Sequential).
- **Static vs. Dynamic**: Does world change while I am thinking?
- **Discrete vs. Continuous**.
- **Single agent vs. Multiagent**.

## 2.4 Agent Structure
- **Simple Reflex Agents**: Condition-Action rules. (If car in front brakes, then brake).
- **Model-Based Reflex Agents**: Keep distinct internal state (Memory).
- **Goal-Based Agents**: Have a goal (Destination). Search for sequence of actions.
- **Utility-Based Agents**: Maximize happiness (not just goal, but how efficient/safe).
- **Learning Agents**: Improve over time.
