```markdown
---
title: "Building a Simple CI/CD Pipeline with Docker, GitHub Actions, and AWS ECS"
date: 2023-10-27 14:30:00 +0000
categories: [DevOps, Cloud Computing]
tags: [ci-cd, docker, github-actions, aws-ecs, infrastructure-as-code]
---

## Introduction

Continuous Integration and Continuous Delivery (CI/CD) are crucial practices for modern software development. They enable teams to automate the process of building, testing, and deploying applications, leading to faster release cycles and improved software quality. This post will guide you through creating a simple CI/CD pipeline using Docker for containerization, GitHub Actions for automation, and AWS ECS (Elastic Container Service) for deployment. We'll focus on a practical, hands-on approach that's suitable for beginners with some cloud computing and development experience.

## Core Concepts

Before diving into the implementation, let's define some core concepts:

*   **Continuous Integration (CI):** The practice of frequently merging code changes into a central repository, followed by automated builds and tests. This helps detect integration issues early.
*   **Continuous Delivery (CD):** The practice of automatically releasing validated code changes to a staging or production environment.
*   **Docker:** A platform for packaging and running applications in containers, providing isolation and portability.
*   **GitHub Actions:** A CI/CD platform integrated into GitHub that allows you to automate workflows based on events in your repository.
*   **AWS ECS (Elastic Container Service):** A fully managed container orchestration service that makes it easy to run, scale, and manage Docker containers on AWS.
*   **Infrastructure as Code (IaC):** Managing and provisioning infrastructure through code, enabling automation and version control. We will use Terraform for IaC in this example.

## Practical Implementation

We will build a simple Python web application, containerize it with Docker, and set up a CI/CD pipeline to deploy it to AWS ECS.

**1. Create a Simple Python Web Application (app.py):**

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World! This is deployed via CI/CD!</p>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

This is a basic Flask application that displays "Hello, World!" when you visit the root URL.

**2. Create a `requirements.txt` file:**

```
Flask==2.0.1
```

This file lists the dependencies for the application.

**3. Create a Dockerfile:**

```dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

This Dockerfile does the following:

*   Starts from a Python 3.9 base image.
*   Sets the working directory to `/app`.
*   Copies the `requirements.txt` file and installs the dependencies.
*   Copies the application code.
*   Exposes port 5000.
*   Runs the `app.py` script.

**4. Set up AWS ECS:**

You'll need an AWS account.  We'll use Terraform to set up the ECS cluster and related resources.  This will create a VPC, Subnets, Security Groups, ECS Cluster, Task Definition, and Load Balancer.

Create a `main.tf` file with the following (replace the placeholders appropriately):

```terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  required_version = ">= 0.13"
}

provider "aws" {
  region = "us-east-1" # Replace with your AWS region
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "ecs-vpc"
  }
}

resource "aws_subnet" "public_subnet_1" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a" # Replace with your AZ
  tags = {
    Name = "ecs-public-subnet-1"
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "us-east-1b" # Replace with your AZ
  tags = {
    Name = "ecs-public-subnet-2"
  }
}


resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "ecs-igw"
  }
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "ecs-public-route-table"
  }
}

resource "aws_route_table_association" "public_subnet_1" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route_table_association" "public_subnet_2" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_route_table.id
}


resource "aws_security_group" "ecs_sg" {
  name        = "ecs-security-group"
  description = "Allow inbound traffic to ECS container"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] #This is very open, limit if possible
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ecs-security-group"
  }
}


resource "aws_ecs_cluster" "default" {
  name = "ecs-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family             = "ecs-task-definition"
  network_mode       = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                = "256" #0.25 vCPU
  memory             = "512" #0.5 GB
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn


  container_definitions = jsonencode([
    {
      name      = "app",
      image     = "YOUR_ECR_REPO_URL:latest", #Replace with your ECR repo URL
      portMappings = [
        {
          containerPort = 5000,
          hostPort      = 5000
        }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name,
          awslogs-region        = "us-east-1", #Replace with your AWS region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}


resource "aws_ecs_service" "app" {
  name            = "ecs-service"
  cluster         = aws_ecs_cluster.default.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.lb_target_group.arn
    container_name   = "app"
    container_port   = 5000
  }

  depends_on = [aws_lb_listener.listener]
}

resource "aws_lb" "app_lb" {
  name               = "application-load-balancer"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_sg.id]
  subnets            = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]


  tags = {
    Name = "application-load-balancer"
  }
}

resource "aws_lb_target_group" "lb_target_group" {
  name        = "lb-target-group"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id

  health_check {
    path = "/"
    port = 5000
    protocol = "HTTP"
  }
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.lb_target_group.arn
  }
}

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name = "ecs-application-logs"
  retention_in_days = 7
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "ecs-task-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Effect = "Allow",
        Sid = ""
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_task_execution_policy" {
  name        = "ecs-task-execution-policy"
  description = "Policy for ECS task execution role"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy_attachment" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_task_execution_policy.arn
}

resource "aws_iam_role" "ecs_task_role" {
  name = "ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Effect = "Allow",
        Sid = ""
      }
    ]
  })
}

```

**Important**: This Terraform configuration is quite extensive and creates a significant number of AWS resources.  Be sure to understand the implications and costs before running `terraform apply`.  Also, replace `YOUR_ECR_REPO_URL` with your actual ECR repository URL.

Run `terraform init`, `terraform plan`, and `terraform apply` to create the AWS infrastructure.

**5.  Create an ECR Repository:**

Create an Elastic Container Registry (ECR) repository in your AWS account to store the Docker image. Take note of the repository URI.

**6. Configure GitHub Actions:**

Create a `.github/workflows/main.yml` file in your repository with the following:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python 3.9
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Build Docker image
        run: docker build -t my-app .

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1 # Replace with your AWS region

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Tag Docker image
        run: docker tag my-app:latest ${{ steps.login-ecr.outputs.registry }}/YOUR_ECR_REPO_NAME:latest # Replace with your ECR repo name

      - name: Push Docker image to Amazon ECR
        run: docker push ${{ steps.login-ecr.outputs.registry }}/YOUR_ECR_REPO_NAME:latest # Replace with your ECR repo name

      - name: Update ECS Task Definition
        run: |
          aws ecs update-service --cluster ecs-cluster --service ecs-service --task-definition ecs-task-definition

```

**Important**: Replace `YOUR_ECR_REPO_NAME` with your ECR repository name. Also, configure the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as GitHub Secrets.  Do NOT commit these credentials directly to your repository.  Go to your GitHub repository's Settings > Secrets > Actions to add them.

## Common Mistakes

*   **Incorrect Dockerfile:**  A poorly written Dockerfile can lead to build failures or performance issues.  Ensure you're using a slim base image and optimizing the layer caching.
*   **Missing Environment Variables:**  If your application relies on environment variables, make sure they are properly configured in the ECS Task Definition.
*   **Incorrect IAM Permissions:**  The IAM roles associated with your ECS Task Definition and Service need the necessary permissions to access AWS resources.
*   **Hardcoding Credentials:**  Never hardcode AWS credentials directly into your code or configuration files. Use GitHub Secrets or AWS Secrets Manager.
*   **Not cleaning up resources:** If deploying a test setup, remember to run `terraform destroy` to avoid unnecessary AWS costs.

## Interview Perspective

When discussing CI/CD in an interview, highlight these points:

*   **Benefits:** Faster release cycles, improved software quality, reduced risk of errors.
*   **Tools:**  Experience with Docker, CI/CD platforms (GitHub Actions, Jenkins, GitLab CI), and cloud providers (AWS, Azure, GCP).
*   **Principles:**  Automation, version control, continuous feedback.
*   **Challenges:**  Handling database migrations, managing infrastructure as code, ensuring security.
*   **Knowledge of the SDLC:** Demonstrate understanding of how CI/CD integrates into the Software Development Lifecycle. Be able to articulate the importance of each stage and how CI/CD aims to make each step faster and more reliable.

## Real-World Use Cases

*   **Web Applications:** Automating the deployment of web applications to production environments.
*   **Microservices:** Deploying and scaling microservices independently.
*   **Mobile Apps:** Building and distributing mobile app builds to app stores.
*   **Infrastructure Updates:** Automating the deployment of infrastructure changes using Infrastructure as Code.
*   **Machine Learning Models:** Training, validating, and deploying Machine Learning models.

## Conclusion

This post demonstrated how to build a simple CI/CD pipeline using Docker, GitHub Actions, and AWS ECS. While this is a basic example, it provides a solid foundation for building more complex and robust CI/CD pipelines. Remember to focus on automation, security, and continuous feedback to achieve the full benefits of CI/CD.  Using Terraform for IaC is crucial for managing your cloud infrastructure effectively.  Always remember to test your pipeline thoroughly and monitor its performance to ensure it is meeting your needs.
```