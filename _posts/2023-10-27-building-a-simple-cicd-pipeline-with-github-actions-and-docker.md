```markdown
---
title: "Building a Simple CI/CD Pipeline with GitHub Actions and Docker"
date: 2023-10-27 14:30:00 +0000
categories: [DevOps, CI/CD]
tags: [github-actions, ci-cd, docker, automation, software-engineering]
---

## Introduction
Continuous Integration and Continuous Delivery (CI/CD) are fundamental practices in modern software development. They enable teams to automate the build, test, and deployment processes, leading to faster release cycles, reduced errors, and improved overall efficiency.  This blog post will guide you through building a simple CI/CD pipeline using GitHub Actions to automate building and pushing a Docker image to Docker Hub.

## Core Concepts
Before diving into the implementation, let's briefly define some key terms:

*   **Continuous Integration (CI):**  The practice of frequently integrating code changes from multiple developers into a shared repository.  Each integration is verified by an automated build and test suite.
*   **Continuous Delivery (CD):**  An extension of CI, where code changes are automatically built, tested, and prepared for release to production. It allows for deploying the software at any time.
*   **Continuous Deployment (CD):**  A further extension of CD, where code changes are automatically deployed to production without explicit human approval.
*   **GitHub Actions:**  A CI/CD platform directly integrated into GitHub repositories. It allows you to automate workflows in response to GitHub events, such as pushes, pull requests, and releases.
*   **Docker:** A platform for developing, shipping, and running applications in containers. Containers isolate applications from their environment, ensuring consistent behavior across different systems.
*   **Docker Hub:** A public registry service by Docker for finding and sharing container images with your team.

## Practical Implementation

Let's create a basic CI/CD pipeline that will:

1.  Trigger a build whenever code is pushed to the `main` branch.
2.  Build a Docker image from the code.
3.  Tag the Docker image with the commit SHA.
4.  Push the Docker image to Docker Hub.

**Step 1: Create a Simple Application**

Let's start with a basic Python "Hello World" application. Create a file named `app.py` with the following content:

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World from CI/CD!"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
```

And a `requirements.txt` file to manage dependencies:

```
Flask==2.3.2
```

**Step 2: Create a Dockerfile**

Next, create a `Dockerfile` in the same directory:

```dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

This Dockerfile uses a slim Python image, installs dependencies, copies the application code, and specifies the command to run the application.

**Step 3: Create a GitHub Repository**

Initialize a Git repository in your project directory and push the code to a new GitHub repository.

**Step 4: Configure Docker Hub**

Create an account on Docker Hub (hub.docker.com) if you don't already have one. Create a new repository on Docker Hub where you will push your image.  Note your Docker Hub username and repository name; you'll need them later.

**Step 5: Create a GitHub Actions Workflow**

In your GitHub repository, create a new directory `.github/workflows`.  Inside this directory, create a YAML file named `ci-cd.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract Git Commit SHA
        id: extract_sha
        run: echo "sha=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            dockerhubusername/your-repository-name:${{ steps.extract_sha.outputs.sha }}
            dockerhubusername/your-repository-name:latest
```

**Explanation of the Workflow:**

*   `name`:  A descriptive name for the workflow.
*   `on`: Defines when the workflow will run. In this case, it's triggered on pushes to the `main` branch.
*   `jobs`: Defines the jobs that will be executed. Here, we have one job named `build-and-push`.
*   `runs-on`: Specifies the operating system to use for the job.
*   `steps`: Defines the individual steps within the job.
    *   `actions/checkout@v3`: Checks out the code from the repository.
    *   `docker/setup-buildx-action@v2`: Sets up Docker Buildx for building multi-platform images if needed.
    *   `docker/login-action@v2`: Logs into Docker Hub using credentials stored as secrets (explained below).
    *   `Extract Git Commit SHA`: Extracts the short commit SHA and makes it available for tagging.
    *   `docker/build-push-action@v4`: Builds and pushes the Docker image to Docker Hub.  Crucially, it tags the image with both the commit SHA and `latest`. Replace `dockerhubusername/your-repository-name` with your actual Docker Hub username and repository name.

**Step 6: Configure GitHub Secrets**

For security, you should not hardcode your Docker Hub credentials in the workflow file. Instead, store them as GitHub secrets.

1.  Go to your GitHub repository settings.
2.  Click on "Secrets and variables" -> "Actions".
3.  Click "New repository secret".
4.  Create two secrets:
    *   `DOCKERHUB_USERNAME`: Your Docker Hub username.
    *   `DOCKERHUB_TOKEN`:  It is recommended to use a Docker Hub Access Token instead of your password. Go to your Docker Hub account settings, and under "Security", generate a new Access Token with "Write, Delete, & Read" access. Copy this token.

**Step 7: Trigger the Pipeline**

Commit and push the `ci-cd.yml` file to your `main` branch. This will automatically trigger the GitHub Actions workflow.

**Step 8: Monitor the Pipeline**

Go to the "Actions" tab in your GitHub repository to monitor the progress of the workflow. You should see the `CI/CD Pipeline` workflow running. If the workflow completes successfully, you should see your Docker image tagged with the commit SHA and `latest` in your Docker Hub repository.

## Common Mistakes

*   **Hardcoding Credentials:**  Never hardcode sensitive information like passwords or API keys directly into your workflow files.  Always use GitHub secrets.
*   **Incorrect Dockerfile Syntax:** A malformed Dockerfile will cause the build to fail.  Double-check your Dockerfile for typos and correct commands.
*   **Missing Dependencies:** Ensure all required dependencies are included in your `requirements.txt` (or equivalent dependency file for other languages).
*   **Insufficient Permissions:**  Ensure your Docker Hub user or token has the necessary permissions (read/write) to push images to the repository.
*   **Not Specifying a Base Image:**  Always start your Dockerfile with a `FROM` instruction to define a base image.
*   **Cache Invalidation:**  Consider using build arguments (`ARG`) in your Dockerfile to invalidate the Docker build cache when necessary. This can be useful when you have changes that aren't detected by the standard Dockerfile `COPY` instruction.

## Interview Perspective

When discussing CI/CD in interviews, be prepared to:

*   **Explain the core concepts of CI/CD:**  Articulate the benefits of automation, faster feedback loops, and reduced risk.
*   **Describe the different stages of a CI/CD pipeline:**  Build, test, deploy.
*   **Discuss different CI/CD tools:**  GitHub Actions, Jenkins, GitLab CI, CircleCI, etc.  Explain the pros and cons of each.
*   **Explain how you handle secrets and configuration management:**  Using environment variables, secrets management tools, and secure storage.
*   **Discuss your experience with Docker and containerization:**  Explain how Docker helps with consistency and portability in CI/CD.
*   **Talk about monitoring and alerting:**  How you track the performance of your pipeline and get notified of failures.
*   **Explain rollback strategies:** Discuss how you handle failed deployments and revert to a previous stable version.
*   **Discuss idempotent deployments:** Ensure that running the deployment multiple times results in the same state.

Key talking points include: Automation, efficiency, faster releases, reduced errors, collaboration, security.

## Real-World Use Cases

CI/CD pipelines are used in various scenarios:

*   **Web Application Development:** Automating the build and deployment of web applications to cloud platforms like AWS, Azure, or Google Cloud.
*   **Mobile App Development:**  Building and deploying mobile apps to app stores (Google Play Store, Apple App Store).
*   **Microservices Architecture:**  Automating the build and deployment of individual microservices.
*   **Infrastructure as Code (IaC):**  Using CI/CD to automate the provisioning and management of infrastructure resources.
*   **Data Science and Machine Learning:** Automating the training, evaluation, and deployment of machine learning models.

## Conclusion

This blog post has provided a practical guide to building a simple CI/CD pipeline using GitHub Actions and Docker. By automating the build, test, and deployment processes, you can significantly improve the efficiency and reliability of your software development workflow. Remember to prioritize security and follow best practices to ensure a robust and maintainable pipeline. This setup is a basic example, but it forms the foundation for much more complex and sophisticated CI/CD workflows. The key is to understand the core principles and adapt them to your specific needs.
```