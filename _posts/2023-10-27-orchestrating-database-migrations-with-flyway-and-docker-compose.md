```markdown
---
title: "Orchestrating Database Migrations with Flyway and Docker Compose"
date: 2023-10-27 14:30:00 +0000
categories: [DevOps, Databases]
tags: [flyway, docker-compose, database-migrations, postgresql, development-workflow]
---

## Introduction

Database migrations are a crucial part of modern software development. They allow us to evolve our database schema in a controlled and reproducible manner.  Manually applying SQL scripts can be error-prone and difficult to manage, especially in complex projects with multiple developers. Flyway is a powerful open-source database migration tool that simplifies this process.  This blog post will guide you through setting up Flyway with Docker Compose for managing PostgreSQL database migrations in a local development environment.  We'll explore the core concepts, provide a practical implementation guide, discuss common pitfalls, and explore real-world use cases.

## Core Concepts

Before diving into the implementation, let's cover the fundamental concepts:

*   **Database Migrations:** Changes made to the database schema (tables, columns, indexes, etc.) over time. These changes are typically implemented as SQL scripts.
*   **Flyway:** An open-source database migration tool that automates the process of applying, reverting, and managing database schema changes. It keeps track of which migrations have been applied and ensures they are applied in the correct order. Flyway supports various databases, including PostgreSQL, MySQL, Oracle, and SQL Server.
*   **Docker Compose:** A tool for defining and running multi-container Docker applications. It allows you to describe your application's services, networks, and volumes in a single `docker-compose.yml` file.  This simplifies the process of setting up and running complex development environments.
*   **Schema Versioning:** Flyway uses a schema version table to track the state of the database. This table stores information about each migration, including its version, description, and execution timestamp.
*   **Migrations Naming Convention:** Flyway expects migrations to follow a specific naming convention: `V<version>__<description>.sql`.  For example, `V1__create_users_table.sql` would be the first migration script. The version number (`V1`) is used to determine the order in which migrations are applied.

## Practical Implementation

Let's create a practical example of using Flyway and Docker Compose to manage PostgreSQL migrations.

**1. Project Structure:**

First, create a directory structure for your project:

```
my-db-migration-project/
├── docker-compose.yml
└── migrations/
    └── V1__create_users_table.sql
    └── V2__add_email_column.sql
```

**2. Docker Compose Configuration (docker-compose.yml):**

Create a `docker-compose.yml` file to define the PostgreSQL database and the Flyway migration service:

```yaml
version: "3.9"
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myuser -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5

  flyway:
    image: flyway/flyway:latest
    depends_on:
      db:
        condition: service_healthy
    environment:
      FLYWAY_URL: jdbc:postgresql://db:5432/mydb
      FLYWAY_USER: myuser
      FLYWAY_PASSWORD: mypassword
      FLYWAY_LOCATIONS: filesystem:/flyway/sql
    volumes:
      - ./migrations:/flyway/sql
    command: migrate

volumes:
  db_data:
```

**Explanation:**

*   **db:** Defines the PostgreSQL database service.
    *   `image`: Specifies the PostgreSQL Docker image.
    *   `environment`: Sets environment variables for the database user, password, and database name.
    *   `ports`: Maps the database port (5432) to the host machine.
    *   `volumes`: Creates a persistent volume for storing database data.
    *   `healthcheck`: Ensures that the database is ready before running the Flyway migrations.

*   **flyway:** Defines the Flyway migration service.
    *   `image`: Specifies the Flyway Docker image.
    *   `depends_on`: Ensures that the database service is running before Flyway starts.
    *   `environment`: Sets environment variables for the database connection URL, user, password, and the location of the migration scripts. `FLYWAY_LOCATIONS` points to the `/flyway/sql` directory within the container, which is mapped to the `./migrations` directory on the host machine.
    *   `volumes`: Mounts the `./migrations` directory on the host machine to the `/flyway/sql` directory in the Flyway container.
    *   `command`: Executes the `migrate` command, which applies the available migrations.

**3. Create Migration Scripts (migrations directory):**

Create the migration scripts in the `migrations` directory.

**V1__create_users_table.sql:**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**V2__add_email_column.sql:**

```sql
ALTER TABLE users ADD COLUMN email VARCHAR(255);
```

**4. Run the Application:**

Open your terminal, navigate to the project directory, and run the following command:

```bash
docker-compose up --build
```

This command will build and start the PostgreSQL database and the Flyway migration service. Flyway will automatically apply the migration scripts to the database.

**5. Verify the Migrations:**

You can verify that the migrations have been applied by connecting to the PostgreSQL database using a client like `psql` or a GUI tool like pgAdmin and inspecting the `users` table.  You should see the `id`, `username`, `created_at`, and `email` columns.  You can also check the `flyway_schema_history` table to see the history of migrations applied.

```bash
docker exec -it my-db-migration-project-db-1 psql -U myuser -d mydb

# Inside psql:
\dt users
\dt flyway_schema_history
```

## Common Mistakes

*   **Incorrect Flyway Configuration:** Ensure that the `FLYWAY_URL`, `FLYWAY_USER`, `FLYWAY_PASSWORD`, and `FLYWAY_LOCATIONS` environment variables are correctly configured in the `docker-compose.yml` file.  Double-check the database connection URL and credentials.
*   **Migration Script Naming Errors:** Adhere to the Flyway migration naming convention (`V<version>__<description>.sql`).  Inconsistent naming can lead to migrations being applied in the wrong order or not being recognized by Flyway.
*   **Database Not Ready:** The Flyway migration service might start before the database is fully initialized. Use the `depends_on` directive with a `condition: service_healthy` in the `docker-compose.yml` file to ensure that Flyway waits for the database to be ready.
*   **Conflicting Migrations:**  If multiple developers are working on the same database, ensure that their migration scripts do not conflict with each other.  Use clear and descriptive migration names and version numbers.
*   **Not Using Version Control:** Database migration scripts should be stored in a version control system (e.g., Git) along with the application code. This allows you to track changes, revert to previous versions, and collaborate effectively with other developers.

## Interview Perspective

When discussing database migrations in interviews, be prepared to address the following:

*   **Importance of Database Migrations:** Explain why database migrations are essential for managing database schema changes in a controlled and reproducible manner.
*   **Flyway's Role:** Describe how Flyway simplifies the process of applying, reverting, and managing database migrations.
*   **Migration Strategies:** Discuss different migration strategies, such as incremental migrations, blue-green deployments, and canary deployments.
*   **Handling Data Migration:** Explain how to handle data migration as part of the schema migration process.  This can involve transforming data from the old schema to the new schema.
*   **Rollback Strategies:** Discuss how to handle rollback scenarios in case a migration fails.
*   **Tooling Familiarity:**  Be prepared to discuss your experience with Flyway or other database migration tools (e.g., Liquibase). Explain how you have used these tools in past projects.
*   **Understanding of the CAP Theorem:** Briefly understanding CAP and how it applies to database choices is valuable.

Key talking points: Idempotency, transactionality, data integrity, schema evolution, and CI/CD integration.

## Real-World Use Cases

*   **Agile Development:**  Database migrations are particularly useful in agile development environments, where database schema changes are frequent and iterative.
*   **Continuous Integration/Continuous Deployment (CI/CD):** Flyway can be integrated into CI/CD pipelines to automate the process of applying database migrations as part of the deployment process.
*   **Microservices Architecture:**  Each microservice may have its own database, requiring independent database migrations.  Flyway can be used to manage these migrations in a decentralized manner.
*   **Legacy Systems:**  Database migrations can be used to modernize legacy databases by applying incremental schema changes and migrating data to new formats.
*   **Multi-Environment Deployments (Dev, Staging, Prod):**  Ensuring consistency of database schemas across different environments is critical. Flyway can ensure migrations are applied in the correct sequence and consistently across all environments.

## Conclusion

Database migrations are a critical aspect of modern software development. Flyway, combined with Docker Compose, provides a powerful and efficient solution for managing PostgreSQL database schema changes in a local development environment. By understanding the core concepts, following the practical implementation guide, avoiding common mistakes, and considering real-world use cases, you can effectively manage database migrations and ensure the integrity and consistency of your data.  This setup greatly improves development workflows and reduces the risk of database-related errors in production.
```