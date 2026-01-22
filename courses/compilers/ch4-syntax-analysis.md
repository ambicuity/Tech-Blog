---
layout: page
title: "Compilers Ch.4: Syntax Analysis"
permalink: /courses/compilers/ch4-syntax-analysis/
---

# Chapter 4: Syntax Analysis (Parsing)

> **Reference**: *Compilers* (Dragon Book), Chapter 4

The Parser is the heart of the frontend. It takes the linear stream of tokens from the Lexer and verifies that they form a valid structure according to the language's grammar, building a **Parse Tree** or **Abstract Syntax Tree (AST)**.

## 4.1 Context-Free Grammars (CFG)
A grammar $G = (T, N, P, S)$ consists of:
-   **Terminals ($T$)**: Basic symbols (tokens like `id`, `if`, `+`).
-   **Non-Terminals ($N$)**: Variables denoting sets of strings (`expr`, `stmt`).
-   **Productions ($P$)**: Rules like `expr -> expr + term`.
-   **Start Symbol ($S$)**.

### Derivation
-   **Leftmost Derivation**: Always expand the leftmost non-terminal.
-   **Rightmost Derivation**: Always expand the rightmost non-terminal. (Used in Bottom-Up parsing).

### Ambiguity
A grammar is **ambiguous** if there is a string that has more than one leftmost derivation (or parse tree).
-   *Example*: `E -> E + E | E * E | id`.
-   String: `id + id * id`.
-   Tree 1: `(id + id) * id`
-   Tree 2: `id + (id * id)` (Correct precedence).
-   *Solution*: Rewrite grammar or use Operator Precedence rules.

---

## 4.2 Top-Down Parsing (LL)
Builds the tree from Root to Leaves. Predicts which production to use next.

### Recursive Descent Parsing
A set of recursive procedures, one for each non-terminal.
```c
void E() {
    T();
    E_prime();
}
```
**Problem**: Cannot handle **Left Recursion** (`E -> E + T`). The function `E()` would call `E()` immediately, causing infinite stack overflow.
-   **Solution**: Elimination of Left Recursion. Rewrite `A -> A \alpha | \beta` as:
    -   `A -> \beta A'`
    -   `A' -> \alpha A' | \epsilon`

### LL(1) Parsing
Uses a **Lookahead** of 1 token to decide.
Requires constructing a **Parsing Table**. We need two helper sets:

1.  **FIRST($\alpha$)**: Set of terminals that can begin strings derived from $\alpha$.
2.  **FOLLOW($A$)**: Set of terminals that can appear immediately to the right of $A$ in some sentential form.

**Algorithm for LL(1) Table**:
-   For production $A \to \alpha$:
    -   For each terminal $a$ in FIRST($\alpha$), add $A \to \alpha$ to `M[A, a]`.
    -   If $\epsilon$ in FIRST($\alpha$), add $A \to \alpha$ to `M[A, b]` for each $b$ in FOLLOW($A$).

---

## 4.3 Bottom-Up Parsing (LR)
Builds the tree from Leaves to Root. Much more powerful than LL. Used by tools like **Yacc** and **Bison**.

### Shift-Reduce Parsing
Maintains a Stack and Input Buffer.
1.  **Shift**: Move input symbol onto stack.
2.  **Reduce**: If top stack elements match a production body ($A \to \beta$), pop $\beta$ and push $A$.
3.  **Accept**: If stack contains only Start Symbol and input is empty.

### Types of LR Parsers
1.  **LR(0)**: No lookahead. Too weak for real languages.
2.  **SLR (Simple LR)**: Uses FOLLOW sets to resolve conflicts.
3.  **LALR (Look-Ahead LR)**: Merges states of Canonical LR. (Industry Standard).
4.  **Canonical LR**: Most powerful, but huge tables.

### The Handle
The "Handle" is the substring in the stack that matches a RHS of a production *and* whose reduction represents one step of the reverse rightmost derivation. Finding the handle is the key to Bottom-Up parsing.

---

## 4.4 Error Recovery
Parsing is not just about accepting valid code, but creating helpful errors for invalid code.
-   **Panic Mode**: Discard input tokens until a "synchronizing" token (like `;` or `}`) is found.
-   **Phrase-level Recovery**: Local correction (insert missing `;`).
