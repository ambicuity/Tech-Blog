```markdown
---
title: "Level Up Your Logging: Structured Logging with Python and Loguru"
date: 2023-10-27 14:30:00 +0000
categories: [Programming, Python]
tags: [structured-logging, python, loguru, observability, debugging]
---

## Introduction
Logging is a crucial aspect of software development. It provides valuable insights into your application's behavior, helping you debug issues, monitor performance, and understand user interactions. Traditional logging often involves simple text-based outputs, which can be difficult to parse and analyze programmatically. Structured logging, on the other hand, uses a standardized format (usually JSON) that makes it easier to search, filter, and aggregate log data. This post will explore structured logging using Python and the Loguru library, providing a practical guide for implementing robust and insightful logging in your projects. We will compare basic logging with structured logging, show implementation examples with Loguru, provide common pitfalls, explore the interview angle, and look at real-world examples.

## Core Concepts

Before diving into implementation, let's understand the core concepts:

*   **Logging:** Recording events that occur during the execution of your program. This can include errors, warnings, informational messages, debug statements, and performance metrics.

*   **Traditional Logging:** Typically involves formatting log messages as simple text strings. While easy to implement initially, these logs become cumbersome to analyze at scale. Think print statements but slightly more organized. Example: `"ERROR - 2023-10-27 14:00:00 - User ID 123 not found."`

*   **Structured Logging:** Involves formatting log messages in a structured format, usually JSON. Each log entry becomes a dictionary with key-value pairs representing different attributes of the event. This makes it easy to parse and query logs programmatically. Example: `{"level": "ERROR", "timestamp": "2023-10-27T14:00:00Z", "message": "User ID not found", "user_id": 123}`

*   **Loguru:** A Python library designed to make logging more convenient and expressive. It offers features like automatic log rotation, colorized output, structured logging, and exception handling. It greatly simplifies configuring and using logging.

*   **Observability:** The ability to understand the internal state of a system from its external outputs, like logs, metrics, and traces. Structured logging is a cornerstone of good observability.

## Practical Implementation

Let's see how to implement structured logging using Python and Loguru:

1.  **Installation:**

    ```bash
    pip install loguru
    ```

2.  **Basic Usage:**

    ```python
    from loguru import logger

    logger.debug("This is a debug message.")
    logger.info("This is an informational message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    ```

    This basic example demonstrates how easy it is to start logging with Loguru. The output by default will be written to standard output.

3.  **Structured Logging (JSON Format):**

    To enable structured logging, you can configure Loguru to output logs in JSON format.

    ```python
    from loguru import logger
    import sys

    logger.add("application.log", format="{message}", serialize=True, level="INFO")
    logger.add(sys.stderr, format="{message}", serialize=True, level="DEBUG")

    user_id = 456
    product_id = "XYZ789"
    logger.info("User viewed product", user_id=user_id, product_id=product_id)
    ```

    This code snippet configures Loguru to output logs to a file named `application.log` and to the standard error stream (`sys.stderr`) using JSON format. The `{message}` format only prints the structured log message. Crucially, `serialize=True` enables the JSON output.  The `user_id` and `product_id` are automatically included in the JSON output as key-value pairs. Example output:

    ```json
    {"message": "User viewed product", "user_id": 456, "product_id": "XYZ789"}
    ```

4.  **Customizing the Log Format:**

    You can customize the log format using various placeholders provided by Loguru.

    ```python
    from loguru import logger

    logger.add("application.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}.{function}:{line} - {message}", serialize=False, level="DEBUG")

    def my_function(x):
        logger.debug(f"Processing value: {x}")

    my_function(10)

    ```

    This example adds timestamps, log levels, module names, function names, and line numbers to the log messages. `serialize=False` now indicates this is NOT structured.

5.  **Handling Exceptions:**

    Loguru makes it easy to log exceptions.

    ```python
    from loguru import logger

    try:
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception("An error occurred during division.")
    ```

    Loguru automatically captures the traceback and includes it in the log message.

6.  **Rotating Log Files:**

    Loguru supports automatic log rotation based on size or time.

    ```python
    from loguru import logger

    logger.add("application.log", rotation="500 MB", retention="10 days", level="INFO")
    ```

    This example rotates the log file when it reaches 500 MB or after 10 days.

## Common Mistakes

*   **Not Using Structured Logging at All:** Sticking with basic print statements or simple text logs makes it difficult to analyze logs at scale.

*   **Logging Too Much or Too Little:**  Finding the right balance is crucial. Too much logging can lead to performance issues and overwhelming log files. Too little logging makes it difficult to debug issues.

*   **Logging Sensitive Information:** Avoid logging passwords, API keys, or other sensitive data. Implement proper redaction or masking techniques.

*   **Inconsistent Logging Levels:** Using inconsistent logging levels can make it difficult to filter and prioritize logs. Stick to a consistent scheme (e.g., DEBUG for development, INFO for normal operation, ERROR/CRITICAL for significant issues).

*   **Not Using Correlation IDs:** In distributed systems, use correlation IDs to track requests across multiple services.  Include the correlation ID in each log message to trace the flow of a request.

## Interview Perspective

Here's what interviewers might ask about logging:

*   **Explain the difference between traditional logging and structured logging.**  Highlight the advantages of structured logging for analysis and observability.
*   **Why is logging important in software development?** Emphasize the importance of logging for debugging, monitoring, and auditing.
*   **How do you choose appropriate logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)?**  Describe the criteria for each level and provide examples.
*   **How would you handle logging in a microservices architecture?**  Discuss the use of correlation IDs, centralized logging systems, and log aggregation tools.
*   **What are the benefits of using a logging library like Loguru?** Mention features like automatic log rotation, structured logging, exception handling, and ease of use.
*   **How do you ensure logs are secure?** Cover topics like avoiding sensitive data, implementing proper access controls, and using secure storage solutions.

Key talking points during an interview are demonstrating that you understand the benefits of logging, the different levels, and how it's applied to various software architecture types. Understanding the proper tools for logging (like Loguru or the standard `logging` library) is also beneficial.

## Real-World Use Cases

*   **E-commerce Platform:** Logging user activity, such as product views, add-to-carts, and purchases. Structured logs can be used to analyze user behavior, identify popular products, and optimize the customer experience.
*   **Financial Application:** Logging transactions, security events, and system errors.  Structured logs are essential for auditing, compliance, and fraud detection.
*   **Cloud Infrastructure Monitoring:** Logging server resource usage, network traffic, and application performance. Structured logs can be used to monitor system health, identify bottlenecks, and detect anomalies.
*   **Machine Learning Pipeline:** Logging data preprocessing steps, model training progress, and evaluation metrics. Structured logs help track experiments, reproduce results, and debug model performance.
*   **CI/CD Pipeline:** Logging build steps, test results, and deployment events. Structured logs are used to monitor the pipeline, identify failures, and track deployments.

## Conclusion

Structured logging is a powerful technique that can significantly improve the observability and debuggability of your applications. Libraries like Loguru make it easy to implement structured logging in Python. By embracing structured logging, you can gain valuable insights into your application's behavior, troubleshoot issues more effectively, and build more robust and reliable systems. Implementing logging from the beginning can save countless hours when you have to fix problems later on.
```