```markdown
---
title: "Building a Basic CI/CD Pipeline with GitHub Actions and Docker"
date: 2024-01-27 13:04:34 +0000
categories: [DevOps, CI/CD]
tags: [github-actions, docker, ci-cd, automation, workflow]
---

## Introduction

Continuous Integration and Continuous Delivery (CI/CD) is a cornerstone of modern software development. It allows teams to automate the process of building, testing, and deploying their applications, leading to faster release cycles, reduced errors, and improved collaboration. This blog post provides a practical guide to building a simple CI/CD pipeline using GitHub Actions and Docker, focusing on automating the build and test phases of your application's lifecycle. We'll use a basic Python application as our example.

## Core Concepts

Before diving into the implementation, let's clarify some key concepts:

*   **Continuous Integration (CI):** The practice of frequently integrating code changes into a shared repository.  Each integration is verified by an automated build and test process, detecting integration errors as quickly as possible.
*   **Continuous Delivery (CD):**  The automation of the release process, ensuring that new code changes can be safely and reliably deployed to production.  This often involves automated testing and deployment stages.
*   **GitHub Actions:** A CI/CD platform directly integrated into GitHub repositories, allowing you to automate workflows based on various events like code pushes, pull requests, or scheduled jobs.
*   **Docker:** A containerization technology that packages an application and its dependencies into a standardized unit for software development. This allows you to run the application consistently across different environments.
*   **Workflow:** A configurable automated process composed of one or more jobs. Workflows are defined in YAML files within the `.github/workflows` directory of your repository.
*   **Job:** A set of steps that are executed on the same runner (virtual machine or container).
*   **Step:** An individual task within a job, such as running a command, installing dependencies, or deploying code.
*   **Runner:** A server that runs your workflows. GitHub provides hosted runners, or you can use your own self-hosted runners.

## Practical Implementation

We'll build a CI/CD pipeline for a simple Python application. The pipeline will:

1.  Trigger on every push to the `main` branch and on pull requests.
2.  Build a Docker image of the application.
3.  Run unit tests within the Docker container.

**1. Setting up the Python Application:**

Create a basic Python application with a unit test.

```python
# app.py
def add(x, y):
  """Adds two numbers."""
  return x + y

if __name__ == "__main__":
  print(add(5, 3))
```

```python
# test_app.py
import unittest
from app import add

class TestApp(unittest.TestCase):

  def test_add(self):
    self.assertEqual(add(2, 3), 5)
    self.assertEqual(add(-1, 1), 0)
    self.assertEqual(add(0, 0), 0)

if __name__ == '__main__':
  unittest.main()
```

**2. Creating a Dockerfile:**

Create a `Dockerfile` to package the application.

```dockerfile
# Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

Create a `requirements.txt` file:

```
# requirements.txt
pytest
```

**3. Defining the GitHub Actions Workflow:**

Create a workflow file named `.github/workflows/ci.yml`:

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3 # checks out the repository

      - name: Set up Python 3.9
        uses: actions/setup-python@v3
        with:
          python-version: 3.9

      - name: Build the Docker image
        run: docker build -t my-python-app .

      - name: Run tests
        run: |
          docker run my-python-app pytest test_app.py
```

**Explanation:**

*   `name`: Defines the name of the workflow (CI/CD Pipeline).
*   `on`: Specifies the events that trigger the workflow (push to main and pull requests targeting main).
*   `jobs`: Defines the jobs to be executed. In this case, we have a single job named `build`.
*   `runs-on`: Specifies the type of runner to use (Ubuntu latest).
*   `steps`: Defines the steps to be executed within the `build` job.
    *   `actions/checkout@v3`: Checks out the repository to the runner.
    *   `actions/setup-python@v3`: Sets up Python 3.9 on the runner.
    *   `docker build`: Builds a Docker image named `my-python-app` using the `Dockerfile`.
    *   `docker run`: Runs the Docker container, executing the pytest command within the container to run the tests.  This command will run the tests defined in `test_app.py`.

**4. Commit and Push the Changes:**

Commit the Python files, Dockerfile, and workflow file to your GitHub repository and push the changes to the `main` branch.

**5. Monitoring the Workflow:**

Go to the "Actions" tab in your GitHub repository to monitor the workflow execution. You'll see the build job running, and if all tests pass, the workflow will succeed.  If any tests fail, the workflow will fail, providing you with feedback on your code.

## Common Mistakes

*   **Incorrect Dockerfile configuration:**  A poorly configured Dockerfile can lead to build failures, missing dependencies, or inconsistent behavior across environments.  Pay close attention to the `FROM`, `COPY`, `RUN`, and `CMD` instructions.
*   **Not caching dependencies:** Installing dependencies for every build can be time-consuming.  Leverage Docker's caching mechanism to speed up builds by caching dependencies in layers.
*   **Ignoring test failures:** A failing CI/CD pipeline indicates a problem in your code.  Always address test failures promptly to maintain the quality of your codebase.
*   **Hardcoding secrets:** Avoid storing sensitive information directly in your workflow files. Use GitHub Secrets to securely manage API keys, passwords, and other credentials.
*   **Insufficient testing:**  Relying solely on unit tests may not be sufficient.  Consider incorporating integration tests, end-to-end tests, and security scans into your CI/CD pipeline.

## Interview Perspective

When discussing CI/CD in interviews, be prepared to:

*   Explain the principles of CI/CD and its benefits.
*   Describe the different stages of a typical CI/CD pipeline (build, test, deploy).
*   Discuss the tools and technologies you have experience with (GitHub Actions, Docker, Jenkins, etc.).
*   Explain how you would troubleshoot a failing CI/CD pipeline.
*   Talk about how you would optimize a CI/CD pipeline for speed and reliability.
*   Discuss security considerations in CI/CD.

Key talking points:

*   **Automation:** CI/CD is all about automating the software delivery process.
*   **Feedback:**  Fast feedback loops are crucial for identifying and resolving issues quickly.
*   **Reliability:**  CI/CD improves the reliability of software releases.
*   **Collaboration:**  CI/CD promotes collaboration among developers, testers, and operations teams.

## Real-World Use Cases

CI/CD is applicable in a wide range of scenarios:

*   **Web applications:** Automating the build, test, and deployment of web applications to cloud platforms like AWS, Azure, or Google Cloud.
*   **Mobile applications:** Automating the build and testing of mobile apps for iOS and Android.
*   **Microservices:**  Building and deploying individual microservices independently.
*   **Infrastructure as Code (IaC):**  Automating the provisioning and configuration of infrastructure using tools like Terraform or Ansible.
*   **Machine Learning (ML):** Automating the training and deployment of ML models.

## Conclusion

This blog post demonstrated how to build a basic CI/CD pipeline using GitHub Actions and Docker. While this is a simplified example, it provides a foundation for building more complex and sophisticated pipelines. By embracing CI/CD principles, you can significantly improve the speed, reliability, and quality of your software development process. Remember to continuously improve and adapt your pipeline as your application evolves.
```