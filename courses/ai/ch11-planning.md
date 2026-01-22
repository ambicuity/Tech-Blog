---
layout: page
title: "AI Ch.11: Automated Planning"
permalink: /courses/ai/ch11-planning/
---

# Chapter 11: Automated Planning

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 11

Search finds a sequence of actions, but it is a "black box". Planning opens the box using logic.

## 11.1 PDDL (Planning Domain Definition Language)
Standard language for planning.
- **State**: Conjunction of fluents. `At(Home) ^ Have(Milk)`.
- **Action**:
    - `Action(Buy(x),`
    - `PRECOND: At(Store) ^ Sells(Store, x)`
    - `EFFECT: Have(x) ^ !Have(Money))`

## 11.2 Planning Algorithms
- **Forward State-Space Search**: Start at Init, try actions to reach Goal. (Heuristic: Number of unsatisfied subgoals).
- **Backward Search**: Start at Goal, regress actions to find Init. (e.g. To have Milk, I must have bought it).

## 11.3 Plan Graph (GraphPlan)
Construct a graph of levels (State level, Action level).
- Used to derive powerful heuristics.
- Can detect mutexes (mutually exclusive actions).

## 11.4 Hierarchical Planning (HTN)
Break high-level actions (`TravelTo(Paris)`) into sub-actions (`BuyTicket`, `GoToAirport`, `Fly`).
- This is how humans plan.
