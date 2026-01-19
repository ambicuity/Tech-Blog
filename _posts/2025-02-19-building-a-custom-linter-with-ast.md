---
layout: post
title: "Building a Custom Linter with AST"
date: 2024-02-29
categories: [Tech, Engineering]
tags: [tech, software, engineering, linter, ast, static analysis]
author: ritesh
---

## Introduction

Linters are essential tools in modern software development. They automatically analyze code to identify potential errors, enforce coding style guidelines, and improve overall code quality. While many excellent linters exist for various programming languages, sometimes you need to enforce specific rules tailored to your project's unique requirements or internal standards. In these cases, building a custom linter can be incredibly beneficial. This blog post explores the process of creating a custom linter using Abstract Syntax Trees (ASTs), offering a practical guide with code examples to get you started. We will focus on Python for our examples, as it has excellent AST support, but the concepts are broadly applicable.

## Core Concepts: AST and Static Analysis

Before diving into the implementation, let's understand the core concepts: Abstract Syntax Trees and static analysis.

**Abstract Syntax Tree (AST):** An AST is a tree representation of the abstract syntactic structure of source code. Each node in the tree represents a construct in the code, such as variables, operators, expressions, or statements. Compilers and interpreters use ASTs to understand and process code. The beauty of ASTs for linting is that they allow you to analyze the *meaning* of the code, not just its textual representation. This enables more sophisticated checks than simple regular expression-based linting.

**Static Analysis:** Static analysis is the process of examining code without executing it. Linters are static analysis tools. By analyzing the source code, they can detect potential problems like syntax errors, unused variables, security vulnerabilities, and style violations. Static analysis contrasts with dynamic analysis, which involves running the code and observing its behavior. ASTs provide a structured and accessible way to perform static analysis.

## Implementation: Building a Python Linter

Let's walk through building a simple custom linter in Python that checks for a specific coding rule: the use of `print` statements. While using `print` for debugging is common, it's often best practice to remove or replace them with proper logging mechanisms before deploying code to production. Our linter will flag any instance of a `print` statement in the code.

**1. Understanding the `ast` Module:**

Python provides a built-in `ast` module that allows you to parse Python code into an AST.  First, you need to understand how to navigate an AST and identify the nodes you're interested in. The following code snippet demonstrates how to parse a Python code string into an AST:

python
import ast

code_string = """
def my_function(x):
    print("Hello, world!")
    return x * 2
"""

tree = ast.parse(code_string)

print(ast.dump(tree))


This code will parse the `code_string` into an AST and then print a string representation of the tree.  The `ast.dump()` function is very useful for understanding the structure of the AST for a given piece of code. Examine the output to identify the node type corresponding to a `print` statement.  You'll likely see something involving `Call` and `Name(id='print')`.

**2. Creating a Node Visitor:**

To traverse the AST and find the nodes we're interested in, we'll create a custom node visitor class. This class will inherit from `ast.NodeVisitor` and override the `visit_` methods for the node types we want to inspect. In our case, we want to inspect `ast.Call` nodes to see if they represent a call to the `print` function.

python
import ast

class PrintStatementVisitor(ast.NodeVisitor):
    def __init__(self):
        self.print_statements = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.print_statements.append(node)
        self.generic_visit(node) # Visit children of the current node


In this code:

*   `PrintStatementVisitor` inherits from `ast.NodeVisitor`.
*   `self.print_statements` is a list to store the `ast.Call` nodes that represent `print` statements.
*   `visit_Call` is called for each `ast.Call` node in the AST.
*   We check if the called function is named 'print'.
*   `self.generic_visit(node)` ensures that we visit the children of the current node.  Without this, the visitor would only inspect the top-level `Call` node and not its arguments or other nested calls.

**3. Using the Visitor:**

Now, let's use the visitor to find `print` statements in a code string.

python
import ast

code_string = """
def my_function(x):
    print("Hello, world!")
    return x * 2

def another_function():
    y = 5
    print(y)
"""

tree = ast.parse(code_string)
visitor = PrintStatementVisitor()
visitor.visit(tree)

if visitor.print_statements:
    print("Found print statements:")
    for node in visitor.print_statements:
        print(f"  Line {node.lineno}, Column {node.col_offset}")
else:
    print("No print statements found.")


This code parses the `code_string`, creates an instance of `PrintStatementVisitor`, visits the AST, and then prints the line and column number of any found `print` statements.

**4. Integrating with Files:**

To make our linter useful, we need to be able to analyze Python files. Here's how you can modify the code to read code from a file:

python
import ast

def check_file_for_prints(filename):
    try:
        with open(filename, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return

    tree = ast.parse(code)
    visitor = PrintStatementVisitor()
    visitor.visit(tree)

    if visitor.print_statements:
        print(f"Found print statements in {filename}:")
        for node in visitor.print_statements:
            print(f"  Line {node.lineno}, Column {node.col_offset}")
    else:
        print(f"No print statements found in {filename}.")


if __name__ == "__main__":
    check_file_for_prints("my_code.py") # Replace with your file


**5. Adding Error Reporting:**

Instead of just printing to the console, a real linter should provide more structured error reporting.  Let's modify the code to return a list of errors, each containing the filename, line number, column offset, and a descriptive message:

python
import ast

class PrintStatementVisitor(ast.NodeVisitor):
    def __init__(self, filename):
        self.print_statements = []
        self.filename = filename

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.print_statements.append({
                'filename': self.filename,
                'lineno': node.lineno,
                'col_offset': node.col_offset,
                'message': "Avoid using print statements in production code. Use logging instead."
            })
        self.generic_visit(node)

def check_file_for_prints(filename):
    errors = []
    try:
        with open(filename, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        errors.append({
            'filename': filename,
            'lineno': 1,
            'col_offset': 0,
            'message': f"File not found: {filename}"
        })
        return errors


    try:
        tree = ast.parse(code)
        visitor = PrintStatementVisitor(filename)
        visitor.visit(tree)
        errors.extend(visitor.print_statements)
    except SyntaxError as e:
       errors.append({
           'filename': filename,
           'lineno': e.lineno,
           'col_offset': e.offset,
           'message': f"Syntax Error: {e.msg}"
       })


    return errors


if __name__ == "__main__":
    errors = check_file_for_prints("my_code.py")

    if errors:
        for error in errors:
            print(f"{error['filename']}:{error['lineno']}:{error['col_offset']} - {error['message']}")
    else:
        print("No issues found.")


This version now handles file not found and syntax errors and returns a consistent error format.

## Expanding the Linter: Beyond `print`

The basic structure we've created can be expanded to check for many other coding rules. Here are some ideas:

*   **Enforcing Naming Conventions:** Check variable and function names against a set of rules (e.g., snake\_case for variables, PascalCase for classes). Use `ast.Name`, `ast.FunctionDef`, and `ast.ClassDef` nodes.
*   **Limiting Complexity:**  Measure the complexity of functions (e.g., cyclomatic complexity) and flag functions that are too complex. This often involves traversing the AST to count branches and loops.
*   **Banning Specific Functions or Modules:**  Prohibit the use of certain functions or modules that might be considered insecure or deprecated. Use `ast.Import`, `ast.ImportFrom`, and `ast.Call` nodes.
*   **Detecting Magic Numbers:** Flag numeric literals that appear directly in code without explanation.

## Conclusion

Building a custom linter with ASTs provides a powerful way to enforce specific coding rules and improve code quality. While it requires understanding the structure of ASTs and writing custom node visitors, the benefits of tailored static analysis can be significant. This blog post has provided a basic framework for creating a Python linter; you can extend it to check for various coding rules and integrate it into your development workflow. Remember to start small, test thoroughly, and gradually add more features as needed. Happy linting!