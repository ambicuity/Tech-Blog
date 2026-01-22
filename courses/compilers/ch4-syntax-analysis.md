---
layout: page
title: "Compilers Ch.4: Syntax Analysis"
permalink: /courses/compilers/ch4-syntax-analysis/
---

# Chapter 4: Syntax Analysis

> **Reference**: *Compilers* (Dragon Book), Chapter 4

The Parser receives tokens and builds the Parse Tree (or AST). It must handle syntax errors gracefully.

## 4.1 Context-Free Grammars
- **Derivation**: Replacing nonterminals to generate a string.
- **Ambiguity**: If a grammar can generate the same string with two different parse trees (e.g., `if E then S else if...`). We must fix grammar to remove ambiguity.

## 4.2 Top-Down Parsing (LL)
Builds tree from Root to Leaves.
- **LL(1)**: Left-to-right scan, Leftmost derivation, 1 token lookahead.
- **Recursive Descent**: Easy to write by hand.
- **Left Recursion**: `A -> A alpha`. Causes infinite loop in Top-Down parsers. Must eliminate.

## 4.3 Bottom-Up Parsing (LR)
Builds tree from Leaves to Root (Reductions).
- **Shift-Reduce Parsing**:
    - **Shift**: Move input symbol to Stack.
    - **Reduce**: If top of stack matches RHS of rule `A -> beta`, pop `beta` and push `A`.
- **LR Parsers**: More powerful than LL. Used by **Yacc / Bison**.
- **SLR** (Simple LR) vs **LALR** (Look-Ahead LR, used in gcc) vs **Canonical LR**.
