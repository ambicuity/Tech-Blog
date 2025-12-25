```markdown
---
title: "Building a Lightweight CI/CD Pipeline with GitHub Actions and Docker Compose"
date: 2023-10-27 14:30:00 +0000
categories: [DevOps, CI/CD]
tags: [github-actions, docker, docker-compose, ci-cd, continuous-integration, continuous-deployment]
---

## Introduction

Continuous Integration and Continuous Delivery (CI/CD) are fundamental practices in modern software development, enabling teams to automate the build, test, and deployment processes. This blog post will guide you through creating a lightweight CI/CD pipeline using GitHub Actions and Docker Compose. This approach is particularly useful for smaller projects or for teams just starting with CI/CD, as it avoids the complexity of heavier solutions like Jenkins or GitLab CI. We will cover setting up automated builds, running tests within Docker containers, and even deploying a simple application to a basic environment.

## Core Concepts

Before diving into the implementation, let's define the key concepts:

*   **Continuous Integration (CI):** The practice of frequently integrating code changes into a shared repository. Each integration is verified by an automated build and test suite.

*   **Continuous Delivery (CD):** An extension of CI, where code changes are automatically prepared for release to production.  This means automatically building, testing, and packaging the application so that it's always in a deployable state.

*   **GitHub Actions:** A CI/CD platform directly integrated into GitHub repositories, allowing you to automate workflows based on events such as code pushes, pull requests, and scheduled tasks.

*   **Docker:** A platform for building, shipping, and running applications in isolated containers. Docker containers package up code and all its dependencies, so the application runs reliably from one computing environment to another.

*   **Docker Compose:** A tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application's services. Then, with a single command, you create and start all the services from your configuration.

## Practical Implementation

Let's create a simple Python application that we'll use to demonstrate our CI/CD pipeline.

**1. Create a Python Application:**

Create a directory for your project and add the following files:

*   `app.py`:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
```

*   `requirements.txt`:

```
flask
```

*   `test_app.py`:

```python
import unittest
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_hello(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), "Hello, World!")

if __name__ == '__main__':
    unittest.main()
```

**2. Create a Dockerfile:**

This Dockerfile will define how our Python application is containerized.

*   `Dockerfile`:

```dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

**3. Create a Docker Compose File:**

This file will define our application's services. In this case, we only have one service: the Python app.

*   `docker-compose.yml`:

```yaml
version: "3.9"
services:
  web:
    build: .
    ports:
      - "5000:5000"
```

**4. Create a GitHub Actions Workflow:**

This workflow will be triggered on every push to the `main` branch. It will build the Docker image, run tests, and potentially deploy the application (we'll just simulate a deployment for simplicity).

*   `.github/workflows/ci-cd.yml`:

```yaml
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
      - uses: actions/checkout@v3

      - name: Set up Python 3.9
        uses: actions/setup-python@v3
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Build the Docker image
        run: docker-compose build

      - name: Run tests
        run: docker-compose run --rm web python test_app.py

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Simulate deployment
        run: echo "Deploying to production..."
```

**Explanation of the GitHub Actions Workflow:**

*   `name: CI/CD Pipeline`:  Defines the name of the workflow.
*   `on:`: Specifies the trigger events. In this case, it triggers on pushes and pull requests to the `main` branch.
*   `jobs:`: Defines the jobs to be executed. We have two jobs: `build` and `deploy`.
*   `build:`: This job builds the Docker image and runs the tests.
    *   `runs-on: ubuntu-latest`: Specifies the runner environment.
    *   `steps:`: Defines the steps to be executed in the job.
        *   `uses: actions/checkout@v3`: Checks out the code from the repository.
        *   `name: Set up Python 3.9`: Sets up the Python environment.
        *   `name: Install dependencies`: Installs the Python dependencies.
        *   `name: Build the Docker image`: Builds the Docker image using `docker-compose build`.
        *   `name: Run tests`: Runs the tests inside the Docker container using `docker-compose run`. The `--rm` flag ensures that the container is removed after the tests are finished.
*   `deploy:`: This job simulates the deployment.
    *   `needs: build`: Specifies that this job depends on the `build` job.
    *   `runs-on: ubuntu-latest`: Specifies the runner environment.
    *   `steps:`: Defines the steps to be executed in the job.
        *   `name: Simulate deployment`: Simulates the deployment by printing a message. In a real-world scenario, this step would involve deploying the Docker image to a cloud provider or a server.

**5. Push to GitHub:**

Commit and push your code to a GitHub repository. GitHub Actions will automatically start the CI/CD pipeline. You can monitor the progress of the workflow in the "Actions" tab of your repository.

## Common Mistakes

*   **Incorrect Dockerfile configuration:** Ensure your Dockerfile properly installs dependencies and sets up the application environment. A common mistake is forgetting to expose the correct port.
*   **Not including tests:** Automated tests are crucial for CI/CD. Neglecting to write tests can lead to deploying broken code.
*   **Ignoring dependency management:**  Always use `requirements.txt` (or equivalent for other languages) to explicitly define your application's dependencies. This ensures consistent builds across different environments.
*   **Insufficient resource limits:**  Docker containers need sufficient resources (CPU, memory) to run properly.  If tests fail or builds are slow, check resource limits.
*   **Hardcoding secrets in the workflow file:** NEVER hardcode sensitive information like API keys or passwords directly in your workflow file. Use GitHub Secrets to securely store and access these values.

## Interview Perspective

When discussing CI/CD pipelines in interviews, be prepared to answer the following:

*   **Explain the benefits of CI/CD:**  Faster development cycles, reduced risk of bugs in production, improved collaboration, and automated deployments.
*   **Describe the components of a CI/CD pipeline:** Source code repository, build server, test environment, deployment environment.
*   **Discuss different CI/CD tools:** Jenkins, GitLab CI, GitHub Actions, CircleCI, Travis CI. Be prepared to explain the pros and cons of each.
*   **Explain different deployment strategies:** Blue/Green deployment, Canary deployment, Rolling deployment.
*   **How do you handle secrets in a CI/CD pipeline?** Discuss the use of secret management tools like HashiCorp Vault or cloud provider secret stores (e.g., AWS Secrets Manager).

Key talking points should include your understanding of the entire process from code commit to deployment, how you ensure code quality through testing, and how you secure sensitive information.  Be able to articulate the tradeoffs involved in choosing different CI/CD tools and deployment strategies.

## Real-World Use Cases

*   **Web application deployment:** Automating the build, test, and deployment of web applications to cloud platforms like AWS, Azure, or Google Cloud.
*   **Mobile app development:** Building and testing mobile apps for iOS and Android, automatically generating builds for distribution.
*   **Microservices deployment:** Deploying individual microservices independently, enabling faster and more frequent releases.
*   **Infrastructure as Code (IaC):**  Using CI/CD to automate the provisioning and management of infrastructure resources using tools like Terraform or Ansible.
*   **Data Science Pipelines:** Automating the training, testing, and deployment of machine learning models.

## Conclusion

This blog post demonstrated how to build a lightweight CI/CD pipeline using GitHub Actions and Docker Compose. This approach is suitable for small to medium-sized projects and provides a solid foundation for automating your software development lifecycle. By embracing CI/CD, you can significantly improve the speed, reliability, and efficiency of your development process. Remember to focus on writing comprehensive tests, managing dependencies effectively, and securing your pipeline with proper secret management techniques. This example provides a basic framework; real-world pipelines often involve more complex configurations, including multiple environments, advanced testing strategies, and integration with other services.
```