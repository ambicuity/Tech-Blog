---
layout: page
title: "AI Ch.21: Deep Learning"
permalink: /courses/ai/ch21-deep-learning/
---

# Chapter 21: Deep Learning

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 21

Deep Learning uses **Neural Networks** with many layers to learn hierarchical representations.

## 21.1 Artificial Neural Networks (ANN)
- **Neuron**: Computes weighted sum of inputs, adds bias, applies activation function (ReLU, Sigmoid).
- **Network**: Layers of neurons. Fully Connected (Dense).
- **Training**: Backpropagation. (Chain Rule to compute gradients backwards).

## 21.2 Convolutional Neural Networks (CNN)
Used for Vision.
- **Convolution Layer**: Slide a small kernel filter over image. Detects edges, shapes.
- **Pooling**: Downsample (Max Pool).
- Translational Invariance.

## 21.3 Recurrent Neural Networks (RNN)
Used for Sequences (Text, Time Series).
- Maintain internal hidden state $h_t$ that depends on $x_t$ and $h_{t-1}$.
- **LSTM (Long Short-Term Memory)**: Solves Vanishing Gradient problem.
- **Transformers**: Attention Is All You Need. (Current SOTA).
