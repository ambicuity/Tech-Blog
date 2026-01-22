---
layout: page
title: "AI Ch.20: Statistical Learning"
permalink: /courses/ai/ch20-statistical-learning/
---

# Chapter 20: Learning Probabilistic Models

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 20

In Ch 19, we learned functions ($y = f(x)$). Now we learn **Probability Distributions** ($P(Y|X)$ or $P(X)$).
This connects Probability (Ch 13) with Learning.

## 20.1 Statistical Learning
-   **Data**: $D = \{d_1, \dots, d_N\}$.
-   **Hypothesis**: A probabilistic model $h_\theta$ parameterized by $\theta$.
-   **Goal**: Find $\theta$ that best explains data.

### Maximum Likelihood Estimation (MLE)
Choose $\theta$ that maximizes the probability of the data.
$$ \theta_{MLE} = \text{argmax}_\theta P(D | \theta) $$
Assuming i.i.d. examples:
$$ L(\theta) = \prod_{j=1}^N P(d_j | \theta) $$
Usually we maximize Log-Likelihood ($\ell$):
$$ \ell(\theta) = \sum_{j=1}^N \log P(d_j | \theta) $$

*   Example: Coin toss. Data = H, H, T.
    *   $P(\text{Heads}) = \theta$.
    *   $L(\theta) = \theta \cdot \theta \cdot (1-\theta) = \theta^2(1-\theta)$.
    *   Maximize: $\theta = 2/3$. (Matches frequency).

---

## 20.2 Naive Bayes Models
The "Hello World" of statistical learning (Spam Filtering).
Assume features $F_1, \dots, F_n$ are independent given Class $C$.
$$ P(C | F_1 \dots F_n) \propto P(C) \prod_i P(F_i | C) $$
-   **Training**: Compute $P(C)$ and $P(F_i | C)$ by counting frequencies in data (use logic from MLE).
-   **Smooth**: Add 1 to counts (Laplace Smoothing) to avoid zero probabilities.

---

## 20.3 Hidden Variables: The EM Algorithm
What if some variables are missing or hidden (Unsupervised)?
**Expectation-Maximization (EM)**:
1.  **E-Step**: Use current parameters $\theta$ to estimate the expected values of hidden variables.
    *   "Fill in the blanks" probabilistically.
2.  **M-Step**: Compute new parameters $\theta'$ to maximize likelihood of the "filled-in" data.
3.  Repeat until convergence.

*   Used for: Gaussian Mixture Models (Clustering), Learning HMMs.
