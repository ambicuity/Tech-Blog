---
title: "Building a Simple CI/CD Pipeline with GitHub Actions for a Python Flask App"
date: 2024-06-09 17:07:28 +0000
categories: [DevOps, CI/CD]
tags: [github-actions, ci-cd, python, flask, deployment, testing]
---

## Introduction

Continuous Integration and Continuous Delivery (CI/CD) are crucial practices in modern software development. They enable teams to automate the software release process, leading to faster feedback loops, improved code quality, and quicker deployments. This post guides you through creating a basic CI/CD pipeline using GitHub Actions to automatically build, test, and potentially deploy a Python Flask application.  We will focus on the fundamentals to give you a solid foundation for more complex pipelines.

## Core Concepts

Before diving into the implementation, let's clarify some key concepts:

*   **Continuous Integration (CI):**  The practice of frequently merging code changes from multiple developers into a central repository. Each merge triggers automated builds and tests to detect integration errors early.
*   **Continuous Delivery (CD):**  An extension of CI, CD automates the process of releasing software changes to an environment (e.g., staging or production) after the code has passed the CI stage.  Crucially, CD doesn't necessarily *automatically* deploy to production; it makes the process readily available and reliably repeatable.  The deployment step might still require manual approval.
*   **GitHub Actions:** A CI/CD platform directly integrated into GitHub. It allows you to automate, customize, and execute your software development workflows directly in your GitHub repository.  Workflows are defined in YAML files and triggered by various events, such as code pushes, pull requests, or scheduled tasks.
*   **Workflow:** A configurable automated process made up of one or more jobs. Workflows are defined by a YAML file checked into your repository.
*   **Job:** A set of steps that execute on the same runner. Each step is either a shell script or a GitHub Action.
*   **Runner:** A server that runs your workflows when they are triggered. Runners can be GitHub-hosted (virtual machines) or self-hosted.
*   **Flask:** A micro web framework written in Python. It's simple to use and well-suited for building web applications and APIs.

## Practical Implementation

Let's create a simple Flask application and then set up a CI/CD pipeline with GitHub Actions.

**1. Create a Flask application (app.py):**

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```

**2. Create a requirements.txt file:**

```
Flask==2.3.2
```

**3. Create a test file (test_app.py):**

```python
import unittest
import app

class TestApp(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()

    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello, World!')

if __name__ == '__main__':
    unittest.main()
```

**4. Create a GitHub repository and push your code.**

Now, let's configure the GitHub Actions workflow.

**5. Create a `.github/workflows` directory in your repository.**

**6. Create a YAML file (e.g., `ci-cd.yml`) inside the `.github/workflows` directory:**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ "main" ] # Or your primary branch name
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python test_app.py

  # (Optional) Add a deployment job if desired.  This example just shows the CI part.
  # deploy:
  #   needs: build # Ensure tests pass before deployment
  #   runs-on: ubuntu-latest
  #   steps:
  #     - name: Deploy to Staging (Example)
  #       run: |
  #         echo "Deploying to staging environment..."
  #         # Add your deployment commands here (e.g., using SSH, Docker, or other deployment tools)
```

**Explanation of the workflow:**

*   **`name: CI/CD Pipeline`:**  Specifies the name of the workflow.
*   **`on:`:**  Defines the triggers for the workflow. In this case, it's triggered on pushes to the `main` branch and pull requests targeting the `main` branch.
*   **`jobs:`:** Defines the jobs to be executed. Here, we have a `build` job.
*   **`runs-on: ubuntu-latest`:** Specifies the runner environment (Ubuntu) for the job.
*   **`steps:`:** Defines the steps to be executed within the job.
    *   **`uses: actions/checkout@v3`:**  Checks out the code from the repository.
    *   **`uses: actions/setup-python@v4`:**  Sets up the Python environment.
    *   **`run: python -m pip install --upgrade pip`:** Upgrades pip to the latest version.
    *   **`run: pip install -r requirements.txt`:** Installs the dependencies listed in `requirements.txt`.
    *   **`run: python test_app.py`:** Executes the tests.
*   **`deploy` (commented out):** This is a placeholder for a deployment job. The `needs: build` line ensures that the deployment job only runs if the build job (and therefore tests) passes successfully. The `run` block would contain your actual deployment commands.  This could involve tools like Docker, SSH, or cloud provider-specific CLIs.

**7. Commit and push the `ci-cd.yml` file to your repository.**

GitHub Actions will automatically detect the workflow and execute it on every push to the `main` branch and on pull requests targeting the `main` branch. You can view the workflow execution status in the "Actions" tab of your GitHub repository.

## Common Mistakes

*   **Forgetting to specify dependencies in `requirements.txt`:** This will cause the build to fail as the required packages will not be available.  Always keep your `requirements.txt` up-to-date.
*   **Incorrectly configured test environment:** Make sure your tests are running in an environment that closely resembles your production environment.  Use environment variables and configuration files appropriately.
*   **Not handling environment variables:**  Secrets and API keys should *never* be hardcoded in your repository. Use GitHub Secrets to securely store these and access them as environment variables in your workflow.
*   **Insufficient testing:**  Don't just test the happy path. Include edge cases, error handling, and security-related tests.
*   **Deploying directly to production without proper testing:**  Always test your changes in a staging environment before deploying to production.  Implement a rollback strategy in case of failures.
*   **Missing `needs` declaration in deployment job:** If a `deploy` job doesn't have a `needs` declaration pointing to the `build` job, the deployment could occur even if the build/test stage failed. This can result in deploying faulty code.

## Interview Perspective

When discussing CI/CD in interviews, be prepared to talk about:

*   **The benefits of CI/CD:**  Faster release cycles, improved code quality, reduced risk of errors, increased team velocity.
*   **The different stages of a CI/CD pipeline:**  Build, test, deploy, monitor.
*   **Different CI/CD tools:**  GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis CI.
*   **Your experience with implementing CI/CD pipelines:**  Describe specific projects where you have used CI/CD and the challenges you faced.
*   **Understanding of Infrastructure as Code (IaC):** CI/CD is often paired with IaC (Terraform, CloudFormation, etc.) to automate infrastructure provisioning.  Demonstrate a basic understanding of how these tools work together.
*   **Concepts like blue/green deployments or canary releases.**  These advanced deployment strategies are often integrated into CI/CD pipelines.
*   **Key Talking Points:** Explain how you've contributed to automating deployment processes, improving testing strategies, and monitoring application health as part of a CI/CD system. Explain how you debug CI/CD failures.

## Real-World Use Cases

CI/CD is applicable to a wide range of projects:

*   **Web applications:** Automatically build, test, and deploy web applications to cloud platforms (AWS, Azure, Google Cloud).
*   **Mobile applications:**  Automate the build and testing of mobile applications for iOS and Android.
*   **Microservices:**  Manage the deployment of individual microservices in a distributed system.
*   **Infrastructure as Code (IaC):**  Automate the provisioning and management of infrastructure resources using tools like Terraform.
*   **Machine Learning Models:**  Automate the training, validation, and deployment of machine learning models.

## Conclusion

This blog post has provided a practical guide to building a simple CI/CD pipeline with GitHub Actions for a Python Flask application.  By automating the build, test, and deployment process, you can improve the speed and quality of your software development lifecycle.  While this example is basic, it provides a strong foundation for building more sophisticated and customized CI/CD pipelines to meet the specific needs of your projects. Remember to focus on robust testing, security, and proper environment management for a successful and reliable CI/CD implementation.