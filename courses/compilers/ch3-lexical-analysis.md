---
layout: page
title: "Compilers Ch.3: Lexical Analysis"
permalink: /courses/compilers/ch3-lexical-analysis/
---

# Chapter 3: Lexical Analysis

> **Reference**: *Compilers* (Dragon Book), Chapter 3

The **Lexical Analyzer** (Scanner) reads the stream of characters and produces a stream of tokens.

## 3.1 Tokens, Patterns, and Lexemes
- **Token**: Abstract symbol (e.g., `id`, `if`, `num`).
- **Pattern**: Rule describing the token (e.g., `[a-zA-Z][a-zA-Z0-9]*`).
- **Lexeme**: The actual string matched (e.g., `count`, `score`).

## 3.2 Regular Expressions
We use RegEx to specify patterns.
- `|` (Union)
- `*` (Kleene Closure - zero or more)
- `+` (One or more)
- `?` (Zero or one)

## 3.3 Finite Automata
RegEx are implemented using Finite Automata.
- **NFA (Nondeterministic Finite Automata)**: Can have multiple transitions for same input, or $\epsilon$-transitions (move without input). Easy to convert RegEx to NFA (Thompson's Construction).
- **DFA (Deterministic Finite Automata)**: One transition per input. No $\epsilon$. Fast execution.

## 3.4 The Lex Algorithm
1.  Write RegEx for language.
2.  Convert RegEx to NFA.
3.  Convert NFA to DFA (Subset Construction).
4.  Minimize DFA states.
5.  Generate C code table. (This is what tools like `lex` or `flex` do).
