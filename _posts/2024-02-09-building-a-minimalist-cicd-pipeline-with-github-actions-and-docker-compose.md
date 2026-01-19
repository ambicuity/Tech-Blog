---
title: "Building a Minimalist CI/CD Pipeline with GitHub Actions and Docker Compose"
date: 2024-02-09 23:23:52 +0000
categories: [DevOps, CI/CD]
tags: [github-actions, docker-compose, ci-cd, automation, testing]
---

## Introduction

Continuous Integration and Continuous Delivery (CI/CD) are crucial for modern software development, enabling faster release cycles and improved software quality. This post explores a practical approach to building a minimalist CI/CD pipeline using GitHub Actions and Docker Compose. We'll focus on automating the process of building, testing, and deploying a simple application using these tools, providing a foundational understanding for implementing CI/CD in your own projects. This pipeline will be triggered on every push to the `main` branch.

## Core Concepts

Before diving into the implementation, let's define the core concepts involved:

*   **Continuous Integration (CI):** The practice of frequently integrating code changes from multiple developers into a shared repository. Automated builds and tests are run on each integration to detect errors early.

*   **Continuous Delivery (CD):** An extension of CI that automates the release process, ensuring that code changes are automatically prepared for deployment to a production environment.

*   **GitHub Actions:** A CI/CD platform integrated directly within GitHub. It allows you to automate workflows triggered by events in your repository, such as pushes, pull requests, or scheduled jobs.

*   **Docker Compose:** A tool for defining and running multi-container Docker applications. It uses a YAML file to configure the application's services, networks, and volumes.

*   **Docker:** A platform that allows you to package, distribute, and run applications in isolated containers. These containers provide a consistent environment regardless of the underlying infrastructure.

## Practical Implementation

Let's create a simple example to illustrate the CI/CD pipeline. We'll use a basic Python "Hello, World!" application within a Docker container.

**1. Application Code (app.py):**

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

**2. Requirements File (requirements.txt):**

```
Flask==2.0.1
```

**3. Dockerfile:**

```dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

**4. Docker Compose File (docker-compose.yml):**

```yaml
version: "3.9"
services:
  web:
    build: .
    ports:
      - "5000:5000"
    restart: always
```

**5. GitHub Actions Workflow (.github/workflows/ci-cd.yml):**

Now, let's define our GitHub Actions workflow. Create a directory named `.github/workflows` in your repository and create a file named `ci-cd.yml`.

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python 3.9
        uses: actions/setup-python@v3
        with:
          python-version: 3.9

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests (Example - Replace with your actual tests)
        run: |
          python -c "print('Running basic smoke test...')"
          python -c "import flask; assert flask.__version__ == '2.0.1'"

      - name: Build Docker image
        run: docker build -t my-app .

  deploy:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Login to Docker Hub (Replace with your registry)
        run: |
          echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u "${{ secrets.DOCKERHUB_USERNAME }}" --password-stdin

      - name: Build and push Docker image
        run: |
          docker build -t ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${GITHUB_SHA::8} .
          docker push ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${GITHUB_SHA::8}

```

**Explanation of the Workflow:**

*   **`name: CI/CD Pipeline`**:  Defines the name of the workflow.
*   **`on: push: branches: [ main ]`**:  Specifies that the workflow is triggered on every push to the `main` branch.
*   **`jobs: build-and-test`**: Defines the first job named `build-and-test`.
    *   **`runs-on: ubuntu-latest`**:  Specifies the runner environment (Ubuntu).
    *   **`steps`**:  A sequence of steps to be executed in the job.
        *   **`actions/checkout@v3`**:  Checks out the code from the repository.
        *   **`actions/setup-python@v3`**: Sets up Python 3.9.
        *   **`pip install -r requirements.txt`**:  Installs the required Python packages.
        *   **`Run tests`**:  Placeholder for your actual test suite.  Here, we have a simple smoke test. You should replace this with more meaningful tests.
        *   **`Build Docker image`**: Builds the Docker image using the Dockerfile.
*   **`jobs: deploy`**: Defines the second job named `deploy`.
    *   **`needs: build-and-test`**: Specifies that this job depends on the successful completion of the `build-and-test` job.
    *   **`if: github.ref == 'refs/heads/main'`**: Ensures the deployment job only runs on pushes to the main branch.
    *   **`steps`**:
        *   **`Login to Docker Hub`**: Logs into Docker Hub using secrets stored in GitHub.  You will need to create secrets named `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` in your GitHub repository settings.
        *   **`Build and push Docker image`**: Builds and pushes the Docker image to Docker Hub, tagging it with the first 8 characters of the Git commit SHA.

**Important Notes:**

*   Replace `${{ secrets.DOCKERHUB_USERNAME }}` and `${{ secrets.DOCKERHUB_TOKEN }}` with your actual Docker Hub username and a personal access token with write access (generate this on Docker Hub). Create these as GitHub secrets in your repository settings (Settings -> Secrets -> Actions).
*   The `Run tests` step in the `build-and-test` job contains a placeholder.  Replace this with your actual test suite. For example, if you were using `pytest`, you would run `pytest` here.
*   This example uses Docker Hub as the container registry. You can adapt it to use other registries like AWS ECR, Google Container Registry, or Azure Container Registry. You'll need to adjust the login and push commands accordingly.
*   The deployment part of this script pushes a new Docker image to Docker Hub. This does *not* automatically deploy the application to an environment. You'll need to add additional steps to deploy the container to a server, Kubernetes cluster, or other deployment platform. A common approach is to use a Docker Compose file on the target server and update it with the new image tag, then restart the Docker Compose stack.

## Common Mistakes

*   **Not Defining Tests:**  Skipping tests is a major pitfall. Comprehensive tests are crucial for catching errors early and ensuring code quality.
*   **Hardcoding Credentials:**  Avoid hardcoding credentials in your workflow files. Use GitHub Secrets to securely store sensitive information.
*   **Insufficient Error Handling:** Implement proper error handling in your workflow to gracefully handle failures and provide informative feedback.
*   **Ignoring Build Context:** Ensure your Dockerfile's build context is appropriate to include necessary files. A missing build context can lead to unexpected errors.
*   **Not Cleaning Up:** In more complex workflows (e.g., using self-hosted runners) it's important to clean up temporary files and resources to avoid resource exhaustion.

## Interview Perspective

Interviewers often ask about your experience with CI/CD, including:

*   **Explain the CI/CD process:** Be prepared to describe the different stages of the pipeline (build, test, deploy) and their purpose.
*   **What tools have you used for CI/CD?** Discuss your experience with tools like GitHub Actions, Jenkins, GitLab CI, CircleCI, etc. Highlight their strengths and weaknesses.
*   **How do you handle secrets in CI/CD?** Explain how you use environment variables or secrets management tools to protect sensitive information.
*   **How do you ensure the quality of your code in the CI/CD pipeline?** Discuss your testing strategies, including unit tests, integration tests, and end-to-end tests.
*   **How do you handle rollbacks in case of a failed deployment?** Explain your rollback strategy, such as using blue/green deployments or canary releases.
*   **What is a Dockerfile and how does Docker Compose work?** Demonstrating knowledge of containerization is key. Be prepared to explain the purpose of a Dockerfile and how Docker Compose orchestrates multi-container applications.

Key talking points:  Automation, testing, security, efficiency, scalability, and continuous improvement. Emphasize how CI/CD contributes to faster release cycles, improved code quality, and reduced risk.

## Real-World Use Cases

*   **Web Applications:** Automating the build, test, and deployment of web applications.
*   **Microservices:** Building and deploying individual microservices independently.
*   **Mobile Apps:** Automating the build and distribution of mobile app binaries.
*   **Infrastructure as Code:** Applying CI/CD principles to infrastructure provisioning and configuration.
*   **Data Science Pipelines:** Automating the training, validation, and deployment of machine learning models.

## Conclusion

This blog post demonstrated a basic CI/CD pipeline using GitHub Actions and Docker Compose. While simplified, it illustrates the core principles of automation, testing, and delivery. By incorporating more sophisticated testing strategies, integrating with deployment platforms, and addressing security considerations, you can build robust CI/CD pipelines that significantly improve your software development process. Remember to tailor your pipeline to the specific needs of your project and environment.