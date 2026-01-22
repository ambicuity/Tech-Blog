---
layout: page
title: "AI Ch.19: Learning"
permalink: /courses/ai/ch19-learning/
---

# Chapter 19: Learning from Examples

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 19

An agent is learning if it improves its performance on future tasks after making observations about the world.

## 19.1 Supervised Learning
Given a training set of `(input, label)` pairs: $(x_1, y_1), \dots, (x_N, y_N)$.
Find a function $h(x)$ (Hypothesis) that approximates the true function $f(x)$.

## 19.2 Decision Trees
- Split data on attribute that maximizes **Information Gain** (reduces Entropy).
- Avoid **Overfitting**: When tree memorizes noise. Use Pruning.

## 19.3 Linear Regression / Classification
- **Regression**: Fit a line $y = wx + b$. Minimize Mean Squared Error (MSE). Gradient Descent.
- **Classification**: Logistic Regression (Sigmoid).

## 19.4 SVM (Support Vector Machines)
Find the hyperplane that separates classes with **Maximum Margin**.
- **Kernel Trick**: Map data to higher dimension to make it linearly separable.
