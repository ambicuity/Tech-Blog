---
layout: post
title: "Building a Production-Ready REST API with FastAPI, Docker, and PostgreSQL"
date: 2024-02-15 20:26:53 +0000
categories: [Backend, DevOps]
tags: [fastapi, docker, postgresql, api, backend, devops, cicd]
---

## Introduction
Building robust and scalable REST APIs is a core skill for any backend engineer. This blog post will guide you through creating a production-ready REST API using FastAPI, a modern, high-performance Python web framework, Docker for containerization, and PostgreSQL for persistent data storage. We'll cover setting up the project, defining API endpoints, connecting to a database, building a Docker image, and highlighting best practices for production deployment.

## Core Concepts

Before diving into the implementation, let's define some key concepts:

*   **REST API (Representational State Transfer Application Programming Interface):** An architectural style that uses standard HTTP methods (GET, POST, PUT, DELETE) to interact with resources.
*   **FastAPI:** A modern, high-performance web framework for building APIs with Python. It features automatic data validation, serialization, and documentation generation using OpenAPI and Swagger UI.
*   **Docker:** A containerization technology that allows you to package an application and its dependencies into a standardized unit for deployment.
*   **PostgreSQL:** A powerful, open-source relational database management system (RDBMS) known for its reliability, data integrity, and advanced features.
*   **ORM (Object-Relational Mapper):** A technique that lets you query and manipulate data from a database using an object-oriented paradigm. We'll be using SQLAlchemy as our ORM.
*   **CRUD (Create, Read, Update, Delete):** The four basic operations performed on persistent data.

## Practical Implementation

Let's build a simple "Task Manager" API with endpoints for creating, reading, updating, and deleting tasks.

**1. Project Setup:**

First, create a project directory and initialize a virtual environment:

```bash
mkdir task-manager-api
cd task-manager-api
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
# venv\Scripts\activate  # On Windows
```

Install the necessary dependencies:

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv
```

**2. Database Configuration:**

Create a `.env` file to store database connection details:

```
DATABASE_URL=postgresql://username:password@hostname:port/database_name
```

Replace `username`, `password`, `hostname`, `port`, and `database_name` with your PostgreSQL credentials. If you don't have a PostgreSQL database set up locally, you can use Docker to run one:

```bash
docker run --name postgres -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -p 5432:5432 -d postgres
```

**3. Database Models (models.py):**

```python
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**4. FastAPI Application (main.py):**

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .models import get_db

app = FastAPI()

@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}", response_model=schemas.Task)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return db_task

@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    return tasks
```

**5. Data Schemas (schemas.py):**

```python
from pydantic import BaseModel
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Task(TaskBase):
    id: int
    completed: bool

    class Config:
        orm_mode = True
```

**6. Dockerfile:**

```dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**7. requirements.txt:**

```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
python-dotenv
```

**8. Build and Run the Docker Image:**

```bash
docker build -t task-manager-api .
docker run -p 8000:8000 task-manager-api
```

Now you can access the API at `http://localhost:8000`. FastAPI automatically generates API documentation at `http://localhost:8000/docs`.

## Common Mistakes

*   **Hardcoding Database Credentials:** Always use environment variables to store sensitive information like database credentials.
*   **Not Handling Exceptions:** Implement proper error handling to catch exceptions and return meaningful error messages to the client.
*   **Lack of Input Validation:** FastAPI provides automatic data validation, but ensure you handle edge cases and custom validation logic.
*   **Ignoring Security Concerns:** Implement authentication and authorization mechanisms to protect your API endpoints.
*   **Poor Logging:** Implement comprehensive logging to track API usage, errors, and performance metrics.
*   **Not using Docker Compose:** For more complex setups (multiple services, persistent volumes), use Docker Compose to manage your containers.

## Interview Perspective

Interviewers often assess your knowledge of:

*   **REST API principles:** Understanding of HTTP methods, status codes, and resource representation.
*   **Framework selection:** Justification for choosing FastAPI over other frameworks (e.g., Flask, Django).
*   **Database design:** Knowledge of relational database concepts, schema design, and ORM usage.
*   **Containerization:** Understanding of Docker concepts, image building, and container orchestration.
*   **Scalability and performance:** Techniques for optimizing API performance and handling high traffic.
*   **Security best practices:** Implementing authentication, authorization, and data validation to protect the API.
*   **Testing:** Implementing unit tests, integration tests, and end-to-end tests to ensure API correctness.

Key talking points:

*   Highlight the benefits of FastAPI (speed, type hinting, automatic documentation).
*   Explain your database schema design and the reasons behind it.
*   Describe your Dockerfile and the steps involved in building the image.
*   Discuss your approach to error handling and logging.
*   Explain how you would scale the API to handle more traffic.
*   Demonstrate your understanding of security best practices.

## Real-World Use Cases

This example provides a foundation for various real-world applications:

*   **Task management systems:**  Extending the API with features like user authentication, project management, and task assignments.
*   **E-commerce platforms:** Managing products, orders, and customer data through API endpoints.
*   **Data analytics platforms:** Ingesting and processing data from various sources through API integrations.
*   **Mobile app backends:** Providing a REST API for mobile apps to access and manage data.
*   **IoT platforms:** Collecting and processing data from IoT devices through API endpoints.

## Conclusion

This blog post demonstrated how to build a production-ready REST API with FastAPI, Docker, and PostgreSQL. We covered the core concepts, practical implementation steps, common mistakes to avoid, interview perspectives, and real-world use cases. By following this guide, you can create robust and scalable APIs that power a wide range of applications. Remember to prioritize security, performance, and maintainability throughout the development process.