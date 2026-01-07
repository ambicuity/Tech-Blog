```markdown
---
title: "Automating PostgreSQL Backups to S3 with pgBackRest and Docker"
date: 2023-10-27 14:30:00 +0000
categories: [DevOps, Databases]
tags: [postgresql, backup, s3, docker, pgbackrest, automation, cloud-storage]
---

## Introduction

Data loss is a nightmare scenario for any organization. Regular backups are crucial for disaster recovery and business continuity. This blog post explores a practical and automated solution for backing up your PostgreSQL databases to Amazon S3 using pgBackRest, a powerful backup and restore tool, packaged within a Docker container. We'll guide you through setting up this system, enabling you to reliably protect your valuable data in the cloud. We'll focus on simplicity and reproducibility, making it easy to integrate into your existing infrastructure.

## Core Concepts

Before we dive into the implementation, let's clarify some key concepts:

*   **PostgreSQL:** A robust, open-source relational database management system (RDBMS) known for its reliability, feature richness, and adherence to standards.
*   **Amazon S3 (Simple Storage Service):** A highly scalable and durable object storage service offered by AWS. S3 provides cost-effective storage for backups, archives, and other data.
*   **pgBackRest:** A dedicated backup and restore utility specifically designed for PostgreSQL. It offers features like incremental backups, parallel processing, and integration with cloud storage solutions like S3.  It excels at managing large database backups.
*   **Docker:** A platform for containerizing applications, ensuring consistency across different environments. This allows us to package pgBackRest and its dependencies into a portable and reproducible unit.
*   **Cron:** A time-based job scheduler in Unix-like operating systems. We'll use cron to schedule the backup process automatically.
*   **WAL (Write-Ahead Logging):**  PostgreSQL's mechanism for ensuring data durability. WAL logs record all changes to the database before they are applied, allowing for recovery in case of a crash. Backing up WAL logs is essential for point-in-time recovery.

## Practical Implementation

Here's a step-by-step guide to setting up automated PostgreSQL backups to S3 using pgBackRest and Docker:

**1. Prerequisites:**

*   An AWS account with an S3 bucket created. Ensure you have the necessary IAM permissions to access the bucket.
*   Docker installed on your server.
*   A running PostgreSQL instance (locally or on a server). You can use another docker container for this part.

**2. Create an S3 Bucket and IAM User**

*   If you haven't already, create an S3 bucket in your AWS account. Note the bucket name and region.
*   Create an IAM user with programmatic access and grant it the `AmazonS3FullAccess` policy for simplicity.  **For production environments, you should limit the IAM role to only the necessary permissions for S3 (e.g., `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`).** Download the IAM user's access key ID and secret access key.  Store these securely.

**3. Create a Dockerfile**

Create a file named `Dockerfile` with the following content:

```dockerfile
FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && apt-get install -y \
    postgresql \
    pgbackrest \
    awscli \
    cron \
    --no-install-recommends

# Set environment variables (replace with your actual values)
ENV AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
ENV AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
ENV AWS_REGION="YOUR_AWS_REGION"
ENV S3_BUCKET="YOUR_S3_BUCKET_NAME"
ENV PG_USER="postgres"
ENV PG_HOST="host.docker.internal" # Host machine PostgreSQL, change when using the same docker network
ENV PG_PORT="5432" # Default PostgreSQL Port

# Create backup script
RUN echo "#!/bin/bash \n\
pgbackrest --stanza=db backup \n\
exit 0" > /backup.sh

RUN chmod +x /backup.sh

# Configure cron to run backup script daily at 2 AM
RUN echo "0 2 * * * root /backup.sh" > /etc/cron.d/pgbackup
RUN chmod 0644 /etc/cron.d/pgbackup

# Create stanza
RUN echo "#!/bin/bash \n\
pgbackrest --stanza=db stanza-create \n\
exit 0" > /stanza.sh

RUN chmod +x /stanza.sh

# Add AWS credentials to AWS CLI config file
RUN mkdir -p /root/.aws
RUN echo "[default]" > /root/.aws/config
RUN echo "region = $AWS_REGION" >> /root/.aws/config
RUN echo "[default]" > /root/.aws/credentials
RUN echo "aws_access_key_id = $AWS_ACCESS_KEY_ID" >> /root/.aws/credentials
RUN echo "aws_secret_access_key = $AWS_SECRET_ACCESS_KEY" >> /root/.aws/credentials


# Start cron service
CMD cron && /bin/bash
```

**Replace the placeholder values for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `S3_BUCKET`, `PG_USER`, `PG_HOST`, and `PG_PORT` with your actual credentials and settings.**

**Important notes:**

*   `PG_HOST=host.docker.internal` in Docker containers allows accessing services running on the host machine.  This assumes you're running PostgreSQL directly on your machine. If you run PostgreSQL inside another Docker container, you'll need to use the container's name or IP address (within the same Docker network).
*  The AWS credentials are being added to the root user's configuration. This may be appropriate for a dedicated backup container, but for broader applications, consider using AWS IAM roles for enhanced security, especially if deploying the container to a managed environment like ECS or Kubernetes.
*  The backup script runs a full backup. For larger databases, consider implementing incremental backups using pgBackRest's `--type=diff` or `--type=incr` options.

**4. Build the Docker Image**

Navigate to the directory containing your `Dockerfile` and run the following command to build the Docker image:

```bash
docker build -t pgbackrest-s3-backup .
```

**5. Create `pgbackrest.conf`**

Create a `pgbackrest.conf` file in the same directory as the Dockerfile.  This file configures pgBackRest:

```ini
[global]
repo1-path=/var/lib/pgbackrest
repo1-s3-bucket=$S3_BUCKET
repo1-s3-endpoint=$AWS_REGION.amazonaws.com

[db]
db-host=$PG_HOST
db-port=$PG_PORT
db-user=$PG_USER
```

**Important**: Use the environment variables directly in the configuration file. Ensure that environment variables are properly passed into the container at runtime. For production environments, consider using Docker Compose or Kubernetes Secrets to manage sensitive configuration data.

**6.  Modify Dockerfile to copy configuration**

Modify your Dockerfile to copy the `pgbackrest.conf` to `/etc/pgbackrest.conf` inside the container and `stanza.sh` to initialize pgbackrest

```dockerfile
# Copy the pgbackrest.conf file
COPY pgbackrest.conf /etc/pgbackrest.conf

# Copy stanza.sh file
COPY stanza.sh /stanza.sh

# Run stanza creation before cron starts
RUN /stanza.sh
```

**7. Run the Docker Container**

Run the Docker container with the necessary environment variables and volume mounts.  For testing, assuming you're running PostgreSQL locally:

```bash
docker run -d \
    -e AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID" \
    -e AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY" \
    -e AWS_REGION="YOUR_AWS_REGION" \
    -e S3_BUCKET="YOUR_S3_BUCKET_NAME" \
    -e PG_USER="postgres" \
    -e PG_HOST="host.docker.internal" \
    -e PG_PORT="5432" \
    --name pgbackrest-backup \
    pgbackrest-s3-backup
```

**Replace the placeholder environment variable values with your actual settings.**

**8. Verify the Setup**

*   Check the Docker container logs using `docker logs pgbackrest-backup` for any errors.
*   Wait for the scheduled backup to run (or trigger it manually by running `docker exec pgbackrest-backup /backup.sh`).
*   Verify that the backup files are uploaded to your S3 bucket.

## Common Mistakes

*   **Incorrect IAM Permissions:** Ensure your IAM user has the necessary permissions to access the S3 bucket.
*   **Missing or Incorrect Environment Variables:** Double-check that all environment variables are correctly set in the Dockerfile and when running the container.  A common mistake is forgetting the AWS region.
*   **Incorrect PostgreSQL Connection Details:** Verify that the `PG_HOST`, `PG_PORT`, and `PG_USER` variables are correct for your PostgreSQL instance. If running PostgreSQL within Docker, ensure the `PG_HOST` is appropriately configured to target the PostgreSQL container.
*   **Cron Scheduling Issues:**  Make sure the cron service is running within the container and that the backup script is executable. Examine `/var/log/syslog` inside the container for cron-related errors.
*  **Forgetting to Create Stanza:** pgBackRest requires you to create a stanza before running backups.  Ensure you have executed the `stanza-create` command.

## Interview Perspective

*   **Explain the purpose of backups and disaster recovery.**
*   **Describe different backup strategies (full, incremental, differential).**
*   **How pgBackRest works and its advantages over other backup solutions.**
*   **How to configure pgBackRest for S3 integration.**
*   **Understanding of Docker and containerization.**
*   **Knowledge of AWS S3 and IAM roles.**
*   **How to troubleshoot backup failures.**
*   **Point-in-time recovery using WAL logs.**
*   **Explain the importance of regular testing of backup and restore procedures.**

Key talking points: emphasize your understanding of data protection principles, the advantages of pgBackRest, and your ability to automate the backup process using Docker and cron.

## Real-World Use Cases

*   **Disaster Recovery:** Recovering from hardware failures, data corruption, or accidental data deletion.
*   **Compliance:** Meeting regulatory requirements for data retention and backup.
*   **Migration:**  Migrating a PostgreSQL database to a new server or cloud environment.
*   **Development and Testing:** Creating backups to restore to development or testing environments for experimentation or debugging.
*   **Archiving:**  Storing historical data for long-term retention and analysis.

## Conclusion

This blog post provided a practical guide to automating PostgreSQL backups to S3 using pgBackRest and Docker. By following these steps, you can ensure the safety and availability of your valuable database data. Remember to tailor the configuration and scripts to your specific needs and environment. Regularly testing your backup and restore procedures is crucial to ensure they function correctly when needed.  Consider exploring more advanced pgBackRest features like incremental backups and parallel processing for larger databases.
```