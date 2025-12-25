```markdown
---
title: "Building a Simple CI/CD Pipeline with Gitlab CI/CD and Docker"
date: 2023-10-27 14:30:00 +0000
categories: [DevOps, CI/CD]
tags: [gitlab-ci, docker, ci-cd, pipeline, automation, development]
---

## Introduction
Continuous Integration and Continuous Delivery (CI/CD) pipelines are crucial for modern software development. They automate the process of building, testing, and deploying applications, resulting in faster release cycles and reduced errors. This post will guide you through building a simple CI/CD pipeline using GitLab CI/CD and Docker. We'll cover the essential concepts, provide a step-by-step implementation guide, and discuss common pitfalls. By the end, you'll have a basic pipeline that automatically builds and deploys a simple application upon code changes.

## Core Concepts
Before diving into the implementation, let's clarify some key concepts:

*   **Continuous Integration (CI):** The practice of frequently integrating code changes from multiple developers into a shared repository. Each integration is verified by an automated build and test process.
*   **Continuous Delivery (CD):** The practice of automatically preparing code changes for release to production. This involves automated testing and deployment to a staging environment.
*   **Continuous Deployment (CD):** An extension of Continuous Delivery where code changes are automatically deployed to production.
*   **.gitlab-ci.yml:** A YAML file at the root of your GitLab repository that defines the CI/CD pipeline configuration. It specifies the stages, jobs, and scripts to be executed.
*   **Stages:** A sequence of jobs that run in a specific order.  For example, a typical pipeline might have stages like "build," "test," and "deploy."
*   **Jobs:** Independent tasks that are executed within a stage. Each job can run a series of commands or scripts.
*   **Docker:** A platform for containerizing applications, allowing you to package an application with all its dependencies into a portable container.
*   **Docker Image:** A read-only template used to create Docker containers.
*   **Docker Container:** A running instance of a Docker image.

## Practical Implementation
Let's create a simple CI/CD pipeline for a basic Python Flask application.

**1. Create a Flask Application (app.py):**

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

**2. Create a requirements.txt file:**

```
Flask
```

**3. Create a Dockerfile:**

```dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

**4. Create a .gitlab-ci.yml file:**

```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  tags:
    - docker

test:
  stage: test
  image: python:3.9-slim-buster
  script:
    - pip install Flask
    - python -c "from app import app; assert app != None"
  tags:
    - docker

deploy:
  stage: deploy
  image: alpine/kubectl:latest
  before_script:
    - apk add --no-cache curl
    - curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
    - chmod +x ./kubectl
    - mv ./kubectl /usr/local/bin/kubectl
    - export KUBECONFIG=$KUBE_CONFIG
  script:
    - kubectl apply -f deployment.yaml
    - kubectl apply -f service.yaml
  variables:
    KUBE_NAMESPACE: your-namespace  # Replace with your Kubernetes namespace
  only:
    - main
  tags:
    - kubernetes
```

**5. Create Kubernetes Deployment and Service files (deployment.yaml and service.yaml):**

**deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-app-deployment
  labels:
    app: flask-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flask-app
  template:
    metadata:
      labels:
        app: flask-app
    spec:
      containers:
      - name: flask-app
        image: your-gitlab-registry-image:latest # Replace with your registry image
        ports:
        - containerPort: 5000
```

**service.yaml:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: flask-app-service
spec:
  selector:
    app: flask-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: LoadBalancer
```

**Explanation:**

*   **build stage:** This stage uses the `docker:latest` image to build a Docker image of our application. It logs into the GitLab container registry using the `CI_REGISTRY_USER` and `CI_REGISTRY_PASSWORD` environment variables, which are automatically provided by GitLab. The image is tagged with the commit SHA (`$CI_COMMIT_SHA`) and pushed to the registry.  The `.gitlab-ci.yml` assumes you have the gitlab shared runner configured to use Docker-in-Docker. The tag `docker` is used to select a runner with docker installed.
*   **test stage:** This stage uses a Python image to run a simple test to verify that the Flask application can be imported.
*   **deploy stage:**  This stage utilizes the kubectl client to deploy the image to a Kubernetes cluster. It downloads the kubectl binary, configures it with your Kubernetes cluster credentials stored in the `$KUBE_CONFIG` environment variable (which you need to configure in GitLab CI/CD settings), and applies the deployment and service manifests. You'll need to configure the `KUBE_CONFIG` variable in your GitLab project's CI/CD settings. Also, you need to replace `your-namespace` with the actual name of your Kubernetes namespace and `your-gitlab-registry-image:latest` with the proper image path and desired tag.  The tag `kubernetes` is used to select a runner with kubectl and Kubernetes configured. The deploy stage is only triggered on the `main` branch.
*   **Variable Substitution:** Ensure that the `image:` field in the `deployment.yaml` file is correctly pointing to your GitLab Container Registry URL with the `:latest` tag.  For example: `registry.gitlab.com/your-group/your-project/flask-app:latest`

**6. Configure GitLab CI/CD Variables:**

Go to your GitLab project's **Settings > CI/CD > Variables** and add the following variables:

*   `KUBE_CONFIG`:  Paste the contents of your Kubernetes configuration file (usually `~/.kube/config`). This allows GitLab to authenticate with your Kubernetes cluster. You should mark this variable as masked to protect the sensitive credentials.
*  `CI_REGISTRY_USER`: This is automatically provided by Gitlab.
*  `CI_REGISTRY_PASSWORD`: This is automatically provided by Gitlab.

**7. Push Your Code:**

Push your code to your GitLab repository. GitLab CI/CD will automatically detect the `.gitlab-ci.yml` file and start the pipeline.

## Common Mistakes

*   **Incorrect Dockerfile:** Make sure your Dockerfile correctly installs all dependencies and copies your application code.
*   **Missing or Incorrect .gitlab-ci.yml:** Double-check the syntax and logic of your `.gitlab-ci.yml` file.  Typos can cause the pipeline to fail.
*   **Authentication Issues:** Verify that your GitLab CI/CD has the necessary permissions to access your container registry and Kubernetes cluster.  Pay special attention to the `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD` and `KUBE_CONFIG` variables.
*   **Network Issues:** Ensure that your GitLab runner can connect to your container registry and Kubernetes cluster. Firewalls can block necessary connections.
*   **Forgetting the `latest` tag:** If you are expecting your application to deploy from the last successful build, be sure the `deploy` stage updates the Docker image with the `latest` tag.
*   **Not configuring the shared runners:** Ensure the shared runners in Gitlab CI/CD are configured to be able to run Docker commands via `docker:dind` service and that a shared runner is configured to use kubectl.
*   **Incorrect YAML syntax:** Indentation is critical in YAML. Ensure that the spacing and indentation are correct in your `.gitlab-ci.yml` file. Use a YAML validator to check for errors.

## Interview Perspective

When discussing CI/CD in interviews, be prepared to answer questions about:

*   The benefits of CI/CD (e.g., faster release cycles, reduced errors, improved collaboration).
*   The different stages of a typical CI/CD pipeline.
*   The tools you have experience with (e.g., GitLab CI/CD, Jenkins, CircleCI, Travis CI).
*   How you handle testing and deployment in your pipelines.
*   How you ensure the security of your CI/CD pipelines.
*   How you troubleshoot pipeline failures.
*   Be able to explain the role of Docker and Kubernetes in a CI/CD pipeline.
*   Discuss how you handle secrets management in your CI/CD pipeline (e.g., using GitLab CI/CD variables with masking).
*   Explain the difference between Continuous Delivery and Continuous Deployment.

Key talking points include your understanding of the automation aspects, the improvement to deployment frequencies and quality, and how CI/CD integrates within a DevOps culture.

## Real-World Use Cases

CI/CD pipelines are used in a wide range of real-world scenarios:

*   **Web Applications:** Automating the build, test, and deployment of web applications.
*   **Mobile Apps:** Building and deploying mobile app updates to app stores.
*   **Microservices:** Deploying and managing microservices-based architectures.
*   **Infrastructure as Code (IaC):** Automating the provisioning and configuration of infrastructure.
*   **Machine Learning:** Training and deploying machine learning models.
*   **Embedded Systems:** Building and testing embedded software.

## Conclusion

This post provided a practical guide to building a simple CI/CD pipeline using GitLab CI/CD and Docker. You learned about the core concepts, implemented a basic pipeline for a Flask application, and explored common mistakes and real-world use cases. By automating your build, test, and deployment processes, you can significantly improve your software development workflow and release high-quality software faster. Remember to adapt and expand upon this example to meet the specific needs of your projects.
```