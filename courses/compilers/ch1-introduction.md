---
layout: page
title: "Compilers Ch.1: Intro"
permalink: /courses/compilers/ch1-introduction/
---

# Chapter 1: Introduction to Compiling

> **Reference**: *Compilers: Principles, Techniques, and Tools* (The Dragon Book), Chapter 1

A **compiler** is a program that reads a program written in one language (the source language) and translates it into an equivalent program in another language (the target language).

## 1.1 The Analysis-Synthesis Model
- **Analysis (Front End)**: Breaks up the source program into constituent pieces and creates an intermediate representation (IR).
- **Synthesis (Back End)**: Constructs the desired target program from the intermediate representation.

## 1.2 Phases of a Compiler
1.  **Lexical Analysis (Scanner)**: Reads stream of characters and groups them into meaningful sequences called **Lexemes**. Produces **Tokens** (e.g., `<id, "position">`).
2.  **Syntax Analysis (Parser)**: Uses the tokens to create a tree-like intermediate representation (**Abstract Syntax Tree** - AST). Checks grammar.
3.  **Semantic Analysis**: Checks logical consistency. (Type checking, declaring variable before use).
4.  **Intermediate Code Generation**: Generates explicit low-level code (Three-address code) for an abstract machine.
5.  **Code Optimization**: Improves intermediate code (faster/smaller).
6.  **Code Generation**: Maps to target machine language (Assembly/Binary).

## 1.3 Cousins of the Compiler
- **Preprocessor**: Macro processing, File inclusion (`#include`).
- **Assembler**: Translates Assembly code to relocatable machine code.
- **Linker**: Combines object files and libraries (`printf`) into a single executable.
- **Loader**: Loads executable into memory.
