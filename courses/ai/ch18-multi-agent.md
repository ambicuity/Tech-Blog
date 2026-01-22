---
layout: page
title: "AI Ch.18: Multi-Agent Systems"
permalink: /courses/ai/ch18-multi-agent/
---

# Chapter 18: Multi-Agent Systems

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 18

What if there are other agents? Logic/Search assumed a static or singly-adversarial environment. Multi-Agent Systems (MAS) handle huge populations, cooperation, and economics.

## 18.1 Game Theory Basics
-   **Nash Equilibrium**: A profile of strategies where no player has incentive to deviate unilaterally.
-   **Prisoner's Dilemma**: Dominant strategy (Defect) leads to suboptimal outcome for both.

## 18.2 Mechanism Design (Inverse Game Theory)
Designing the rules of the game so that selfish agents achieve a global goal (Social Welfare).
-   **Auctions**:
    -   **English Auction**: Ascending bids.
    -   **Vickrey Auction (Second-Price Sealed-Bid)**: Winner pays the *second* highest price. Truth-telling is a dominant strategy!

## 18.3 Cooperative AI
-   **Contract Net Protocol**: Manager announces task. Bidders send proposals. Manager awards contract.
-   **Swarm Intelligence**: Simple local rules lead to complex global behavior (Ant Colony Optimization).
