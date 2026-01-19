```markdown
---
title: "Building a Simple CI/CD Pipeline with GitHub Actions and Docker"
date: 2024-06-08 03:58:13 +0000
categories: [DevOps, CI/CD]
tags: [github-actions, docker, ci-cd, automation, workflow]
---

## Introduction

Continuous Integration and Continuous Delivery (CI/CD) is a crucial practice in modern software development, allowing teams to automate the build, test, and deployment processes. This reduces errors, speeds up delivery, and improves overall efficiency. This blog post will guide you through creating a basic CI/CD pipeline using GitHub Actions and Docker. We'll focus on automating the process of building a Docker image from a simple Python application and pushing it to a container registry. This example will use Docker Hub, but the principles can be adapted for other registries like AWS ECR or Google Container Registry.

## Core Concepts

Before we dive into the implementation, let's define the key concepts involved:

*   **Continuous Integration (CI):** The practice of frequently integrating code changes from multiple developers into a shared repository. Automated builds and tests are run to ensure code quality and prevent integration issues.

*   **Continuous Delivery (CD):** The practice of automating the software release process, enabling frequent and reliable deployments to various environments (e.g., staging, production).

*   **GitHub Actions:** A CI/CD platform directly integrated into GitHub repositories. It allows you to automate workflows based on various events, such as code pushes, pull requests, or scheduled tasks.

*   **Docker:** A containerization technology that allows you to package an application and its dependencies into a portable container. This ensures consistent execution across different environments.

*   **Docker Hub:** A public registry for Docker images. It allows you to store and share Docker images with the community or within your organization. Other registries are available from cloud providers.

*   **YAML:** A human-readable data serialization language commonly used to define configuration files, including GitHub Actions workflows.

## Practical Implementation

Let's build a simple CI/CD pipeline for a basic Python application.

**1. Create a Python Application:**

Create a file named `app.py` with the following content:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
  return "Hello, world!"

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0')
```

This is a very simple Flask application that returns "Hello, world!" when accessed.

**2. Create a `requirements.txt` File:**

List the application dependencies in a file named `requirements.txt`:

```
Flask
```

**3. Create a `Dockerfile`:**

This file defines how to build the Docker image:

```dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

This `Dockerfile` does the following:

*   Uses a base image of Python 3.9.
*   Sets the working directory to `/app`.
*   Copies the `requirements.txt` file and installs the dependencies using `pip`.
*   Copies the application code.
*   Exposes port 5000 (the port Flask listens on).
*   Sets the command to run the application.

**4. Create a GitHub Repository:**

Create a new repository on GitHub and push the `app.py`, `requirements.txt`, and `Dockerfile` files.

**5. Create a GitHub Actions Workflow:**

Create a directory named `.github/workflows` in your repository.  Inside this directory, create a file named `ci-cd.yml` (or any other name you prefer with a `.yml` extension).

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build the Docker image
        run: docker build . -t my-app

  push-to-dockerhub:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Log in to Docker Hub
        run: |
          echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u "${{ secrets.DOCKERHUB_USERNAME }}" --password-stdin
      - name: Build and Push the Docker image
        run: |
          docker build . -t ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}
          docker push ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}
          docker tag ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }} ${{ secrets.DOCKERHUB_USERNAME }}/my-app:latest
          docker push ${{ secrets.DOCKERHUB_USERNAME }}/my-app:latest
```

This workflow is triggered on pushes to the `main` branch and pull requests targeting the `main` branch.  It consists of two jobs:

*   **`build`:**  Builds the Docker image.

*   **`push-to-dockerhub`:**  Logs in to Docker Hub using secrets, builds the Docker image with a tag based on the Git commit SHA, pushes the image to Docker Hub, and then also tags and pushes a `latest` version.

**6. Configure GitHub Secrets:**

In your GitHub repository, go to "Settings" -> "Secrets and variables" -> "Actions".  Add the following secrets:

*   `DOCKERHUB_USERNAME`: Your Docker Hub username.
*   `DOCKERHUB_TOKEN`: A Docker Hub access token with write permissions (generate this on Docker Hub under your profile settings -> Security -> Access Tokens).

**7. Push the Changes:**

Push the `.github/workflows/ci-cd.yml` file to your GitHub repository. This will trigger the CI/CD pipeline.

**8. Verify the Pipeline:**

Go to the "Actions" tab in your GitHub repository. You should see the workflow running.  Once it completes successfully, check your Docker Hub repository.  You should see the newly pushed image with the commit SHA tag and the `latest` tag.

## Common Mistakes

*   **Incorrect Dockerfile Syntax:** Errors in your `Dockerfile` can lead to build failures. Double-check your commands and syntax.

*   **Missing Dependencies:** Ensure that all dependencies are listed in the `requirements.txt` file (or equivalent for other languages/package managers).

*   **Incorrect Secret Configuration:** Double-check that your GitHub secrets are correctly named and contain the correct values. Ensure the user associated with the Dockerhub token has appropriate permissions.

*   **Network Issues:** If your build process requires external network access (e.g., downloading dependencies), ensure that the build environment has proper network connectivity.

*   **Not tagging images:** Pushing "latest" alone without using commit SHAs or semantic versions makes rollback or debugging significantly harder.

## Interview Perspective

During an interview, be prepared to discuss the following aspects of CI/CD:

*   **Benefits of CI/CD:** Reduced time to market, improved code quality, increased automation, and faster feedback loops.
*   **CI/CD Tools:** Familiarity with popular CI/CD platforms like GitHub Actions, Jenkins, GitLab CI, CircleCI, and Travis CI.
*   **Docker and Containerization:** Understanding of containerization principles, Docker concepts, and how Docker fits into a CI/CD pipeline.
*   **Workflow Design:** Ability to design a CI/CD workflow for a given application or project, including the build, test, and deployment steps.
*   **Troubleshooting:** Ability to identify and resolve common issues in a CI/CD pipeline.
*   **Specific use-cases and examples** Be prepared to talk about projects you've worked on that used CI/CD.

Key talking points: Explain how your team used CI/CD to automate deployments, reduce errors, and improve release velocity.  Mention specific tools and technologies you used. Also be prepared to discuss the trade-offs.

## Real-World Use Cases

CI/CD is applicable in a wide range of scenarios:

*   **Web Applications:** Automating the deployment of web applications to cloud platforms like AWS, Azure, or Google Cloud.
*   **Mobile Applications:** Building and distributing mobile applications to app stores or internal distribution channels.
*   **Microservices:** Deploying and managing microservices architectures, where frequent updates and deployments are common.
*   **Infrastructure as Code (IaC):** Automating the deployment of infrastructure changes using tools like Terraform or CloudFormation.
*   **Data Science and Machine Learning:** Automating the training and deployment of machine learning models.

## Conclusion

This blog post provided a practical guide to building a simple CI/CD pipeline using GitHub Actions and Docker. By automating the build, test, and deployment processes, you can significantly improve your software development workflow and deliver value to your users more quickly and reliably. Remember to tailor the pipeline to your specific needs and continuously improve it as your project evolves. Understanding CI/CD principles is essential for any modern software engineer.
```