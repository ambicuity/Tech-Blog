---
title: "Building a Simple REST API with Go and SQLite: A Practical Guide"
date: 2024-06-21 21:02:31 +0000
categories: [Programming, Go]
tags: [go, golang, rest-api, sqlite, database, http, beginner-friendly]
---

## Introduction

Building REST APIs is a fundamental skill for any backend developer. Go, with its simplicity and efficiency, is an excellent choice for creating robust and performant APIs. This blog post will guide you through building a simple REST API using Go and SQLite, a lightweight and embedded database. We'll create an API for managing a basic "tasks" list, covering CRUD (Create, Read, Update, Delete) operations. This tutorial is aimed at beginners and intermediate developers looking to solidify their Go API development skills.

## Core Concepts

Before diving into the implementation, let's cover the key concepts:

*   **REST API:**  REST (Representational State Transfer) is an architectural style for designing networked applications. REST APIs use standard HTTP methods (GET, POST, PUT, DELETE) to interact with resources.
*   **HTTP Methods:**
    *   **GET:** Retrieves a resource.
    *   **POST:** Creates a new resource.
    *   **PUT:** Updates an existing resource completely.
    *   **DELETE:** Deletes a resource.
*   **JSON:** JavaScript Object Notation, a lightweight data-interchange format that is easy for humans to read and write, and easy for machines to parse and generate.
*   **SQLite:** A self-contained, serverless, zero-configuration, transactional SQL database engine. It's ideal for small to medium-sized applications and development purposes.
*   **Go Standard Library (`net/http`):** Provides the necessary tools for building HTTP servers and clients.
*   **Go Modules:** A dependency management system for Go projects, ensuring reproducible builds.
*   **CRUD Operations:**  The four basic functions of persistent storage: Create, Read, Update, and Delete.

## Practical Implementation

Let's build our "tasks" API step-by-step.

**Step 1: Setting up the Project**

First, create a new directory for your project and initialize Go modules:

```bash
mkdir go-tasks-api
cd go-tasks-api
go mod init example.com/go-tasks-api
```

This creates a `go.mod` file that will track our dependencies.

**Step 2: Defining the Task Struct**

Create a file named `main.go` and define the `Task` struct:

```go
package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"

	_ "github.com/mattn/go-sqlite3"
)

type Task struct {
	ID          int    `json:"id"`
	Title       string `json:"title"`
	Description string `json:"description"`
	Completed   bool   `json:"completed"`
}

var db *sql.DB

func main() {
	// Database setup
	var err error
	db, err = sql.Open("sqlite3", "./tasks.db")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS tasks (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			title TEXT NOT NULL,
			description TEXT,
			completed BOOLEAN DEFAULT FALSE
		)
	`)
	if err != nil {
		log.Fatal(err)
	}

	// Route Handlers
	http.HandleFunc("/tasks", getTasksHandler)
	http.HandleFunc("/tasks/", taskHandler) // For specific task operations

	// Start the server
	fmt.Println("Server listening on port 8080...")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
```

**Explanation:**

*   We import necessary packages like `database/sql`, `encoding/json`, `net/http`, and the SQLite driver.
*   We define the `Task` struct with fields for ID, Title, Description, and Completed status.  The `json:"..."` tags are used for JSON serialization/deserialization.
*   We declare a global variable `db` of type `*sql.DB` to hold the database connection.
*   The `main` function initializes the SQLite database, creates the `tasks` table if it doesn't exist, and sets up HTTP route handlers.

**Step 3: Implementing the `getTasksHandler`**

```go
func getTasksHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodGet {
		tasks, err := getTasks()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(tasks)
	} else if r.Method == http.MethodPost {
		createTaskHandler(w, r)
	} else {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func getTasks() ([]Task, error) {
	rows, err := db.Query("SELECT id, title, description, completed FROM tasks")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var tasks []Task
	for rows.Next() {
		var task Task
		err := rows.Scan(&task.ID, &task.Title, &task.Description, &task.Completed)
		if err != nil {
			return nil, err
		}
		tasks = append(tasks, task)
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return tasks, nil
}
```

**Explanation:**

*   `getTasksHandler` handles both GET (for retrieving all tasks) and POST (for creating a new task) requests to `/tasks`.
*   `getTasks` queries the database and returns a slice of `Task` structs.  It handles potential errors gracefully.
*   The handler sets the `Content-Type` header to `application/json` and encodes the `tasks` slice as JSON.

**Step 4: Implementing `createTaskHandler`**

```go
func createTaskHandler(w http.ResponseWriter, r *http.Request) {
	var task Task
	err := json.NewDecoder(r.Body).Decode(&task)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	result, err := db.Exec("INSERT INTO tasks (title, description) VALUES (?, ?)", task.Title, task.Description)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	id, err := result.LastInsertId()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	task.ID = int(id) // Set the ID of the created task

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated) // Set status code to 201 Created
	json.NewEncoder(w).Encode(task)
}
```

**Explanation:**

*   `createTaskHandler` decodes the JSON body of the request into a `Task` struct.
*   It inserts the new task into the database.
*   It retrieves the ID of the newly inserted row and sets the `ID` field of the `Task` struct.
*   Sets the HTTP status code to 201 (Created) and encodes the created task as JSON.

**Step 5: Implementing `taskHandler` (GET, PUT, DELETE by ID)**

```go
func taskHandler(w http.ResponseWriter, r *http.Request) {
	idStr := r.URL.Path[len("/tasks/"):]
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "Invalid task ID", http.StatusBadRequest)
		return
	}

	switch r.Method {
	case http.MethodGet:
		getTaskByIDHandler(w, r, id)
	case http.MethodPut:
		updateTaskHandler(w, r, id)
	case http.MethodDelete:
		deleteTaskHandler(w, r, id)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func getTaskByIDHandler(w http.ResponseWriter, r *http.Request, id int) {
	var task Task
	row := db.QueryRow("SELECT id, title, description, completed FROM tasks WHERE id = ?", id)
	err := row.Scan(&task.ID, &task.Title, &task.Description, &task.Completed)

	if err == sql.ErrNoRows {
		http.Error(w, "Task not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(task)
}

func updateTaskHandler(w http.ResponseWriter, r *http.Request, id int) {
    var task Task
    err := json.NewDecoder(r.Body).Decode(&task)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

	_, err = db.Exec("UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?", task.Title, task.Description, task.Completed, id)

    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    w.WriteHeader(http.StatusOK)
    fmt.Fprintf(w, "Task with ID %d updated successfully", id)

}

func deleteTaskHandler(w http.ResponseWriter, r *http.Request, id int) {
	_, err := db.Exec("DELETE FROM tasks WHERE id = ?", id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "Task with ID %d deleted successfully", id)
}

```

**Explanation:**

*   `taskHandler` extracts the task ID from the URL path.
*   It uses a `switch` statement to handle GET, PUT, and DELETE requests based on the HTTP method.
*   `getTaskByIDHandler` retrieves a task by its ID from the database.
*   `updateTaskHandler` updates the task in the database.
*   `deleteTaskHandler` deletes the task from the database.
*   Each handler handles errors appropriately.

**Step 6: Running the Application**

```bash
go run main.go
```

Your API is now running on port 8080. You can use tools like `curl` or Postman to test the endpoints.

## Common Mistakes

*   **Not Handling Errors:**  Ignoring errors can lead to unexpected behavior and difficult debugging.  Always check for errors and handle them gracefully.
*   **SQL Injection:**  Never directly concatenate user input into SQL queries. Use parameterized queries to prevent SQL injection vulnerabilities. The code above uses parameterized queries, which is the safe and recommended approach.
*   **Incorrect HTTP Status Codes:**  Using the wrong HTTP status codes can confuse clients.  Use appropriate codes like 200 OK, 201 Created, 400 Bad Request, 404 Not Found, and 500 Internal Server Error.
*   **Ignoring Resource Management:**  Remember to close database connections and result sets to avoid resource leaks.  Use `defer` to ensure resources are closed even if errors occur.
*   **Poor Validation:** Validate incoming data to ensure it meets your requirements. This can prevent unexpected errors and security vulnerabilities.

## Interview Perspective

During interviews, you might be asked about:

*   **RESTful API design principles:** Explain the key characteristics of REST and how your API adheres to them.
*   **HTTP methods:** Describe the different HTTP methods and their intended use.
*   **Database interaction:** Explain how you interact with the database, including querying and updating data.
*   **Error handling:** Discuss your error handling strategy and how you ensure the API is robust.
*   **Security considerations:**  Mention how you protect against common vulnerabilities like SQL injection.
*   **Code structure and organization:**  Be prepared to explain your code structure and why you chose certain design patterns.
*   **Testing strategies:** Mention how you would test your API.

Key talking points:

*   Emphasize your understanding of REST principles.
*   Demonstrate your ability to handle errors gracefully.
*   Highlight your awareness of security best practices.
*   Show that you can write clean, well-organized, and maintainable code.

## Real-World Use Cases

This simple API can be extended to more complex scenarios:

*   **Task Management Applications:**  Expand the API to include features like task prioritization, due dates, and user assignments.
*   **Todo List Applications:** This is already a good starting point for a Todo List application.
*   **Microservice Backend:**  Integrate this API into a larger microservice architecture.
*   **Data Collection Endpoint:**  Use the API to collect data from various sources.
*   **Simple CMS:** The principles here can be extended for a very simple CMS.

## Conclusion

This blog post provided a step-by-step guide to building a simple REST API with Go and SQLite. You learned about fundamental concepts, implemented CRUD operations, and addressed common pitfalls. By understanding these principles, you can build more complex and robust APIs for a variety of applications. Remember to practice, experiment, and continue learning to master your Go API development skills. Good luck!