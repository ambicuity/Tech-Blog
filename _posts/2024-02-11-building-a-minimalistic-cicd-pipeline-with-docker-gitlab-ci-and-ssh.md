```markdown
---
title: "Building a Minimalistic CI/CD Pipeline with Docker, GitLab CI, and SSH"
date: 2024-02-11 07:47:07 +0000
categories: [DevOps, CI/CD]
tags: [ci-cd, docker, gitlab-ci, ssh, automation, pipeline]
---

## Introduction

Continuous Integration and Continuous Delivery (CI/CD) pipelines are essential for modern software development. They automate the process of building, testing, and deploying code, leading to faster release cycles and improved software quality. While sophisticated CI/CD systems can be complex, a minimal, functional pipeline can be built with just a few core tools: Docker, GitLab CI, and SSH. This blog post will guide you through building such a pipeline, enabling you to automate deployments to a remote server.

## Core Concepts

Before diving into the implementation, let's define the key concepts involved:

*   **Continuous Integration (CI):** The practice of frequently integrating code changes into a shared repository. Automated builds and tests are run upon each commit to verify the changes.
*   **Continuous Delivery (CD):** The practice of automating the release process, enabling frequent and reliable deployments.
*   **Docker:** A platform for building, running, and shipping applications in containers. Containers provide a consistent and isolated environment for applications.
*   **GitLab CI:** A built-in CI/CD tool within GitLab that allows you to define pipelines using YAML files (.gitlab-ci.yml).
*   **SSH (Secure Shell):** A cryptographic network protocol for secure communication between two computers. In this context, it allows GitLab CI to remotely execute commands on the deployment server.
*   **.gitlab-ci.yml:** The configuration file that defines the CI/CD pipeline for a GitLab project. It specifies the stages, jobs, and scripts to be executed.

## Practical Implementation

This example demonstrates deploying a simple "Hello World" web application written in Python to a remote server.

**1. Project Setup:**

*   Create a new GitLab project (e.g., `simple-deploy`).
*   Create a Python file `app.py`:

    ```python
    from flask import Flask
    app = Flask(__name__)

    @app.route("/")
    def hello():
        return "Hello World!"

    if __name__ == "__main__":
        app.run(debug=True, host='0.0.0.0', port=8080)
    ```

*   Create a `requirements.txt` file:

    ```
    Flask
    ```

*   Create a `Dockerfile`:

    ```dockerfile
    FROM python:3.9-slim-buster

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY app.py .

    EXPOSE 8080

    CMD ["python", "app.py"]
    ```

**2. Set up SSH Key on Deployment Server:**

*   On your *deployment server* (the server where the application will run), generate an SSH key pair:

    ```bash
    ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa_deploy
    ```

    *Important:* Use an empty passphrase ("") for the private key for automated access. This comes with security considerations, discussed later.
*   Copy the *public* key (`~/.ssh/id_rsa_deploy.pub`) to the `~/.ssh/authorized_keys` file on your deployment server:

    ```bash
    cat ~/.ssh/id_rsa_deploy.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    ```

**3. Configure GitLab CI Variables:**

*   Go to your GitLab project's Settings -> CI/CD -> Variables.
*   Add the following variables:
    *   `SSH_PRIVATE_KEY`: The *content* of the *private* key file (`~/.ssh/id_rsa_deploy`) from your deployment server. Ensure this is *masked* and *protected* in GitLab CI. This is the most sensitive piece of information.
    *   `SSH_USER`: The username to use when connecting to the deployment server (e.g., `ubuntu`).
    *   `SSH_HOST`: The IP address or hostname of your deployment server.
    *   `DEPLOY_PATH`: The absolute path on the deployment server where you want to deploy the application (e.g., `/home/ubuntu/deploy`).

**4. Create `.gitlab-ci.yml`:**

Create a `.gitlab-ci.yml` file in the root of your GitLab project with the following content:

```yaml
stages:
  - build
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

deploy:
  stage: deploy
  image: ubuntu:latest
  before_script:
    - apt-get update -yq
    - apt-get install -yq openssh-client rsync
    - mkdir -p ~/.ssh
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - ssh-keyscan $SSH_HOST >> ~/.ssh/known_hosts
    - chmod 400 ~/.ssh/known_hosts
  script:
    - ssh -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST "mkdir -p $DEPLOY_PATH"
    - rsync -avz --delete --exclude '.git*' -e "ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa" . $SSH_USER@$SSH_HOST:$DEPLOY_PATH
    - ssh -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST "docker stop my-app || true && docker rm my-app || true && docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA && docker run -d -p 80:8080 --name my-app $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"
  tags:
    - shell
  dependencies:
    - build
  only:
    - main # Or your main branch name

```

**Explanation of `.gitlab-ci.yml`:**

*   **Stages:** Defines two stages: `build` and `deploy`.
*   **Build Stage:**
    *   Uses a Docker image to build a Docker image of the application.
    *   Logs in to the GitLab Container Registry.
    *   Builds the Docker image and tags it with the commit SHA.
    *   Pushes the image to the GitLab Container Registry.
    *   Requires a `docker` tag on the GitLab Runner.
*   **Deploy Stage:**
    *   Uses an Ubuntu image.
    *   Installs necessary packages (openssh-client, rsync).
    *   Sets up SSH access by:
        *   Creating the `.ssh` directory.
        *   Writing the `SSH_PRIVATE_KEY` to `~/.ssh/id_rsa`.
        *   Setting the correct permissions on the private key.
        *   Adding the SSH host key to `~/.ssh/known_hosts` to avoid "host key verification failed" errors (using `ssh-keyscan`).
    *   Deploys the code to the deployment server using `rsync` over SSH.  This copies all files (except those in `.git*` directories) to the `$DEPLOY_PATH`.
    *   Executes commands on the deployment server via SSH to:
        *   Stop and remove any existing container named `my-app`.
        *   Pull the latest Docker image from the GitLab Container Registry.
        *   Run the new Docker image as a detached container, mapping port 80 on the host to port 8080 in the container.
    *   Requires a `shell` tag on the GitLab Runner (the runner needs shell access to the deployment server).
    *   Depends on the `build` stage to complete successfully.
    *   Only runs on commits to the `main` branch.

**5. Deployment Server Setup (Simplified Example)**

On the *deployment server*:

```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

You may also need to add your user to the docker group to avoid using `sudo` with `docker` commands.

**6. Commit and Push:**

Commit and push all the files to your GitLab repository. The CI/CD pipeline should automatically trigger.

## Common Mistakes

*   **Incorrect SSH Key Setup:** Ensure the public key is correctly added to `~/.ssh/authorized_keys` and the private key is correctly stored in GitLab CI variables.  Permissions on the private key on the runner are critical (600).
*   **Missing Dependencies:** Make sure the necessary packages (openssh-client, rsync, Docker) are installed on both the GitLab Runner and the deployment server.
*   **Incorrect Paths:** Double-check the paths in the `.gitlab-ci.yml` file (e.g., `DEPLOY_PATH`).
*   **Docker Registry Authentication:**  If you're using a private Docker registry, ensure proper authentication is configured in the `.gitlab-ci.yml` file and the registry allows pulls from your runner's IP address.
*   **Security Issues:** Storing SSH private keys in GitLab CI variables is inherently risky. Consider using more secure methods like HashiCorp Vault for secrets management. *Never commit private keys to the repository.*

## Interview Perspective

When discussing this topic in an interview, be prepared to discuss:

*   The benefits of CI/CD.
*   The roles of Docker, GitLab CI, and SSH in the pipeline.
*   Security considerations regarding SSH key management.
*   Alternative deployment strategies (e.g., using Kubernetes, Ansible, or other automation tools).
*   How to scale the pipeline for larger applications.
*   How to monitor the pipeline and application.
*   Trade-offs between simplicity and security/scalability in this minimal approach.

Key talking points should include security, automation, and scalability. Mention the importance of key rotation and least privilege principles when handling SSH keys. Explain the limitations of `rsync` for large deployments and suggest alternative tools like Ansible or infrastructure-as-code solutions.

## Real-World Use Cases

This minimalistic CI/CD pipeline is suitable for:

*   Deploying small web applications or APIs.
*   Automating deployments to development or staging environments.
*   Personal projects where you want to automate deployments.
*   Quickly prototyping CI/CD workflows.

For larger and more complex applications, consider using more robust tools and platforms, such as Kubernetes, Helm, Ansible, Terraform, and dedicated CI/CD platforms like Jenkins, CircleCI, or GitLab CI with auto-scaling runners.

## Conclusion

This blog post demonstrated how to build a simple yet functional CI/CD pipeline using Docker, GitLab CI, and SSH. While it has limitations in terms of security and scalability, it provides a valuable starting point for automating deployments and streamlining your software development process. Remember to prioritize security and consider more advanced tools as your application grows. This foundation will allow you to understand the core concepts before moving to more robust solutions.
```