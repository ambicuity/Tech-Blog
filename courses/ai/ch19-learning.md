---
layout: page
title: "AI Ch.19: Learning"
permalink: /courses/ai/ch19-learning/
---

# Chapter 19: Learning from Examples (Supervised Learning)

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 19

Learning is the process of improving performance based on data.
**Supervised Learning**: Given training set $(x_i, y_i)$, find function $h$ such that $h(x) \approx y$.

## 19.1 Decision Trees
A tree where:
-   **Internal Node**: Test on an attribute.
-   **Branch**: Outcome of test.
-   **Leaf**: Class label.

### Inducing Trees (ID3 Algorithm)
Which attribute should we split on? The one that is most informative.
**Entropy**: Measure of uncertainty.
$$ H(S) = - \sum p_i \log_2 p_i $$
*   If set is 50/50 +/-, Entropy = 1 (Max uncertainty).
*   If set is 100/0, Entropy = 0.

**Information Gain**: Expected reduction in entropy.
$$ Gain(S, A) = H(S) - \sum_{v \in Values(A)} \frac{|S_v|}{|S|} H(S_v) $$
*   **Algorithm**:
    1.  Calculate Gain for all attributes.
    2.  Pick max Gain. Make it root.
    3.  Partition data. Recurse.

---

## 19.2 Overfitting
A tree can memorize the training data (including noise), leading to poor generalization.
*   **Pruning**: Remove branches that do not statistically improve classification (Chi-squared test).
*   **Random Forests**: Ensemble of many trees trained on random subsets of data.

---

## 19.3 Linear Models
### Linear Regression
$$ h_w(x) = w_0 + w_1 x_1 + \dots $$
**Loss Function**: Squared Error $L(w) = \sum (y_i - h_w(x_i))^2$.
**Gradient Descent**: Update weights to move down the error surface.
$$ w_j \leftarrow w_j + \alpha (y - h(x)) x_j $$

### Logistic Regression
For classification. Output probability using Sigmoid function.
$$ h_w(x) = \frac{1}{1 + e^{-w^T x}} $$
