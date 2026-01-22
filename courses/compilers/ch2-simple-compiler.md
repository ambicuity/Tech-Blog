---
layout: page
title: "Compilers Ch.2: Simple Compiler"
permalink: /courses/compilers/ch2-simple-compiler/
---

# Chapter 2: A Simple One-Pass Compiler

> **Reference**: *Compilers* (Dragon Book), Chapter 2

To understand the big picture, we build a simple translator for infix expressions (e.g., `9-5+2`) to postfix code (stack machine instructions).

## 2.1 Syntax Definition
We use **Context-Free Grammars (CFG)**.
- **Productions**: `list -> list + digit`
- **Terminals**: Basic symbols (`+`, `-`, `0..9`).
- **Nonterminals**: Variables (`list`, `digit`).
- **Start Symbol**: Where derivation begins.

## 2.2 Syntax-Directed Translation
We attach **actions** (code snippets) to grammar rules.
```
expr -> expr + term { print('+') }
      | expr - term { print('-') }
      | term
```
When we reduce `expr + term`, we execute `print('+')`.

## 2.3 Parsing
For this simple grammar, we can write a **Recursive Descent Parser**.
- Create a function for each nonterminal.
- `void expr() { term(); while(lookahead == '+') { match('+'); term(); print('+'); } }`

## 2.4 A Simple Lexer
The parser needs tokens, not characters.
The lexer skips whitespace and groups digits into numbers.
```c
if (isdigit(peek)) {
    v = 0;
    do { v = v*10 + (peek-'0'); } while(isdigit(peek));
    return NUM;
}
```
