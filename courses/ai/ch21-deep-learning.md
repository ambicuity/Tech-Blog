---
layout: page
title: "AI Ch.21: Deep Learning"
permalink: /courses/ai/ch21-deep-learning/
---

# Chapter 21: Deep Learning

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 21

Deep Learning (DL) means Neural Networks with many hidden layers.

## 21.1 Feedforward Networks
A Directed Acyclic Graph.
-   **Perceptron**: $a = g(W^T x + b)$.
    -   $g$: Activation function. ReLU ($max(0,z)$), Sigmoid ($1/(1+e^{-z})$).
    -   ReLU is preferred today (solves Vanishing Gradient).

### Backpropagation (The Chain Rule)
How do we train W? Minimize Loss $L$.
$$ \frac{\partial L}{\partial w} = \frac{\partial L}{\partial a} \cdot \frac{\partial a}{\partial z} \cdot \frac{\partial z}{\partial w} $$
1.  **Forward Pass**: Compute outputs.
2.  **Backward Pass**: Compute gradients from output layer to input layer.
3.  **Update**: $W \leftarrow W - \eta \nabla L$.

---

## 21.2 Convolutional Neural Networks (CNN)
Prior: **Spatial Locality**. Pixels near each other matter.
1.  **Convolution**: $S(i, j) = (I * K)(i, j) = \sum \sum I(m, n) K(i-m, j-n)$.
    -   Learns filters (Edges, textures).
2.  **Pooling**: Downsample. MaxPool ($2 \times 2$). Provides invariance to small translations.

## 21.3 Recurrent Neural Networks (RNN)
Prior: **Sequential Data**. $x_t$ depends on $x_{t-1}$.
Unroll through time.
-   **Vanishing Gradient**: Gradients decay exponentially over long sequences.
-   **LSTM (Long Short-Term Memory)**: Uses "Gates" (Input, Forget, Output) to control information flow.
    -   $c_t = f_t c_{t-1} + i_t \tilde{c}_t$. (Cell state acts as a superhighway for gradients).

## 21.4 Transformers (Attention)
Current SOTA (GPT, BERT).
-   Discard recurrence. Use **Self-Attention**.
-   $Attention(Q, K, V) = softmax(\frac{QK^T}{\sqrt{d}}) V$.
-   "How much does word A relate to word B?"
