---
title: "Building Scalable Data Pipelines with Prefect and Docker Compose"
date: 2024-08-14 02:16:40 +0000
categories: [DevOps, Data Engineering]
tags: [prefect, docker, docker-compose, data-pipeline, orchestration, airflow-alternative]
---

## Introduction

Data pipelines are the backbone of modern data-driven organizations. They automate the process of extracting, transforming, and loading (ETL) data from various sources into a data warehouse or data lake for analysis and decision-making.  While tools like Apache Airflow are prevalent, Prefect offers a compelling alternative with a Python-first approach and a focus on observability and ease of use. This post explores how to leverage Prefect and Docker Compose to build scalable and reproducible data pipelines. We'll focus on setting up a local development environment that closely mimics a production deployment.

## Core Concepts

Before diving into the practical implementation, let's clarify some essential concepts:

*   **Prefect:** A Python-based workflow orchestration engine. It allows you to define your data pipelines as Python code and manage their execution, monitoring, and retries. Prefect uses *flows* to represent pipelines and *tasks* to represent individual steps within the pipeline.

*   **Docker:** A platform for building, shipping, and running applications in containers. Containers package an application and its dependencies together, ensuring consistent execution across different environments.

*   **Docker Compose:** A tool for defining and running multi-container Docker applications. It uses a YAML file to configure the services, networks, and volumes required for your application.

*   **Flow:** A Python function decorated with `@flow`. A flow represents your entire data pipeline.

*   **Task:** A Python function decorated with `@task`. A task represents a single step within your data pipeline.

*   **Orchestration:** The automated management and coordination of computer systems, applications, and services. In the context of data pipelines, orchestration involves scheduling, monitoring, and managing the execution of flows and tasks.

## Practical Implementation

Let's build a simple data pipeline that fetches data from an API, transforms it, and saves it to a local file. We'll use Prefect to orchestrate this pipeline and Docker Compose to create a reproducible development environment.

**1. Project Setup:**

Create a project directory:

```bash
mkdir prefect-docker-pipeline
cd prefect-docker-pipeline
```

**2. Docker Compose File (docker-compose.yml):**

This file defines the services our pipeline will use.  We'll need a Prefect agent to execute our flows and a Prefect UI to monitor them.  We will also use a local file system for persistence.

```yaml
version: "3.9"
services:
  prefect:
    image: prefecthq/prefect:2.10.14-python3.9
    restart: unless-stopped
    ports:
      - "4200:4200" # Prefect UI
    volumes:
      - prefect_data:/root/.prefect
    environment:
      PREFECT_API_URL: http://prefect:4200/api
      PREFECT_UI_URL: http://prefect:4200
      PREFECT_LOGGING_EXTRA_LOGGERS: "['docker']" # Enable docker logging
    depends_on:
      - postgres

  agent:
    image: prefecthq/prefect:2.10.14-python3.9
    restart: unless-stopped
    depends_on:
      - prefect
    environment:
      PREFECT_API_URL: http://prefect:4200/api
      PREFECT_LOGGING_EXTRA_LOGGERS: "['docker']" # Enable docker logging
    command: prefect agent start -q default

  postgres:
    image: postgres:14
    restart: unless-stopped
    environment:
      POSTGRES_USER: prefect
      POSTGRES_PASSWORD: prefect
      POSTGRES_DB: prefect
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  prefect_data:
  postgres_data:
```

**Explanation:**

*   `prefect`:  Runs the Prefect server and UI. It maps port 4200 to your local machine.
*   `agent`: Runs the Prefect agent, which polls the Prefect server for flows to execute.  It is configured to use the `default` queue.
*   `postgres`: Runs a PostgreSQL database for Prefect to store its metadata.
*   `PREFECT_API_URL`:  Tells the agent and UI where the Prefect API is located.
*   `volumes`:  Persists data between container restarts.

**3. Python Code (pipeline.py):**

Create a file named `pipeline.py` in the same directory as `docker-compose.yml`:

```python
from prefect import flow, task
import requests
import json
import os

@task(retries=3, retry_delay_seconds=5)
def fetch_data(url: str) -> dict:
    """Fetches data from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise  # Re-raise the exception for Prefect to handle retry

@task
def transform_data(data: dict) -> list:
    """Transforms the data (e.g., filters or aggregates)."""
    # Example: Extract only user IDs
    return [user["id"] for user in data]


@task
def save_data(data: list, filename: str = "output.json") -> None:
    """Saves the data to a file."""
    filepath = os.path.join(os.getcwd(), filename) # Use the current directory
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filepath}")


@flow(name="Data Pipeline")
def main_flow(url: str = "https://jsonplaceholder.typicode.com/users"):
    """Main data pipeline flow."""
    raw_data = fetch_data(url)
    transformed_data = transform_data(raw_data)
    save_data(transformed_data)


if __name__ == "__main__":
    main_flow() # You can run it locally for testing

```

**Explanation:**

*   `fetch_data`: Fetches data from a specified URL using the `requests` library. Includes error handling and retry logic.
*   `transform_data`: Transforms the fetched data. In this example, it extracts user IDs.
*   `save_data`: Saves the transformed data to a JSON file.
*   `main_flow`:  The main flow that orchestrates the tasks.  It defines the data pipeline. The `@flow` decorator turns the function into a Prefect flow. The default parameter allows to easily change parameters.

**4. Run the Pipeline:**

1.  Start the Docker Compose environment:

    ```bash
    docker-compose up -d
    ```

2.  Register the flow with Prefect:

    First, install Prefect: `pip install prefect`
    Then, execute:

    ```bash
    prefect flow register --path ./pipeline.py
    ```
    This will register the flow, and the Prefect agent will pick it up for execution.

3.  Monitor the execution in the Prefect UI at `http://localhost:4200`. You should see your "Data Pipeline" flow and its runs.

**5. Trigger the flow directly from the UI:**

In the Prefect UI, navigate to the Flows section, select your "Data Pipeline" flow, and click "Run".

## Common Mistakes

*   **Incorrect `PREFECT_API_URL`:**  Ensure the `PREFECT_API_URL` in the `docker-compose.yml` file correctly points to the Prefect server.
*   **Missing Dependencies:** Make sure all necessary Python packages (e.g., `requests`) are installed in your environment. You can achieve this using a `requirements.txt` file and including it in the Docker image if you choose to containerize the Python code itself for production.
*   **Not Handling Errors:**  Properly handle errors within your tasks to prevent pipeline failures. Prefect's retry mechanism can help with transient errors.
*   **Hardcoding Credentials:**  Never hardcode sensitive information like API keys or database passwords directly in your code. Use environment variables or Prefect's secrets management.
*   **Not Defining Resources:**  For computationally intensive tasks, define resource limits (CPU, memory) in Prefect to prevent resource exhaustion.

## Interview Perspective

Interviewers often ask about your experience with data pipeline orchestration tools. Be prepared to discuss:

*   **Your choice of Prefect (or alternatives like Airflow):**  Explain why you selected Prefect for a particular project, highlighting its benefits (e.g., Python-first approach, ease of use, observability).
*   **Flow and Task Design:**  Describe how you structure your flows and tasks, considering factors like modularity, reusability, and error handling.
*   **Scalability and Reliability:**  Explain how you design your pipelines to handle large datasets and ensure they are resilient to failures.  Discuss retry strategies, resource management, and monitoring.
*   **Dockerization:** Explain how Docker helps with reproducibility and deployment of the pipeline.

Key Talking Points:

*   Prefect's first-class Python support simplifies pipeline development.
*   Prefect's UI provides excellent visibility into pipeline execution.
*   Prefect's retry mechanisms and error handling contribute to pipeline reliability.
*   Docker Compose facilitates local development and testing.

## Real-World Use Cases

*   **E-commerce:**  Ingesting and processing customer order data from various sources (website, mobile app, payment gateway) to update inventory, generate reports, and personalize marketing campaigns.
*   **Financial Services:**  Collecting and analyzing market data from multiple exchanges to identify trading opportunities and manage risk.
*   **Healthcare:**  Processing patient data from electronic health records (EHRs) to identify trends, improve patient outcomes, and optimize resource allocation.
*   **Marketing Analytics:** Collecting data from various sources like websites, ad platforms, and CRM systems to generate reports on campaign performance, identify target audiences, and improve marketing ROI.

## Conclusion

This post demonstrated how to build a scalable data pipeline using Prefect and Docker Compose. By leveraging Prefect's Python-first approach and Docker Compose's ability to create reproducible environments, you can streamline your data engineering workflows and build robust, maintainable data pipelines. Remember to prioritize error handling, resource management, and security best practices to ensure the reliability and scalability of your pipelines in production. Embrace Prefect as a tool for its simplicity and ability to handle complex workflows effectively.