---
title: "Building a Resilient Microservice with Circuit Breakers in Go"
date: 2024-03-11 08:56:57 +0000
categories: [Programming, Go]
tags: [go, microservices, circuit-breaker, resilience, error-handling]
---

## Introduction
In the world of microservices, resilience is paramount.  A single failing service can trigger a cascade of failures, bringing down your entire application. Circuit breakers are a crucial design pattern for preventing this, allowing your system to gracefully handle errors and degraded performance in dependent services. This blog post will guide you through building a simple microservice in Go, complete with a circuit breaker to enhance its resilience. We'll be using the `github.com/sony/gobreaker` library.

## Core Concepts
Before diving into the code, let's define the key concepts:

*   **Microservices:**  An architectural style that structures an application as a collection of loosely coupled services, modeled around a business domain.
*   **Resilience:** The ability of a system to recover from failures and continue functioning, even when some components are experiencing issues.
*   **Circuit Breaker:** A software design pattern that prevents an application from repeatedly trying to execute an operation that's likely to fail. It acts like an electrical circuit breaker, "opening" the circuit when a certain failure threshold is reached, and only "closing" it again after a period of successful operations.
*   **Open State:** The circuit breaker stops all requests from being executed.
*   **Closed State:** The circuit breaker allows all requests to be executed.
*   **Half-Open State:** After a timeout period in the Open state, the circuit breaker allows a limited number of requests to be executed to test if the downstream service is available.
*   **Fallback:**  A strategy for handling failures. When the circuit breaker is open, instead of failing, the service can execute a fallback, which might return cached data, a default value, or a general error message.

## Practical Implementation
Let's build a simple microservice that depends on another (potentially unreliable) service.  Our service will fetch a user profile from a "User Service" (which we'll simulate).  We'll then implement a circuit breaker to protect our service.

**1. Project Setup:**

Create a new Go project:

```bash
mkdir circuit-breaker-example
cd circuit-breaker-example
go mod init circuit-breaker-example
go get github.com/gorilla/mux github.com/sony/gobreaker
```

**2.  `main.go` - Our Main Service:**

```go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"time"

	"github.com/gorilla/mux"
	"github.com/sony/gobreaker"
)

// UserProfile represents the user profile data.
type UserProfile struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

// userServiceURL is the URL of the (potentially unreliable) User Service.
const userServiceURL = "http://localhost:8081/user"

// gobreakerConfig defines the configuration for the circuit breaker.
var gobreakerConfig = gobreaker.Settings{
	Name:        "user-service",
	MaxRequests: 5,            // Number of requests allowed to pass when the circuit breaker is half-open.
	Interval:    1 * time.Minute, // The period of the circuit breaker to clear the ConsecutiveFailures.
	Timeout:     30 * time.Second, // The period of the circuit breaker to switch to half-open.
	ReadyToTrip: func(counts gobreaker.Counts) bool {
		failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
		return counts.Requests >= 10 && failureRatio >= 0.6 // Trip if 60% of requests fail after 10 requests
	},
}

var cb *gobreaker.CircuitBreaker

func main() {
	cb = gobreaker.NewCircuitBreaker(gobreakerConfig)

	r := mux.NewRouter()
	r.HandleFunc("/profile/{id}", getUserProfileHandler).Methods("GET")

	log.Fatal(http.ListenAndServe(":8080", r))
}

func getUserProfileHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	userIDStr := vars["id"]
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		http.Error(w, "Invalid user ID", http.StatusBadRequest)
		return
	}

	// Execute the request through the circuit breaker.
	profile, err := getUserProfileWithCircuitBreaker(userID)
	if err != nil {
		http.Error(w, "Failed to retrieve user profile: "+err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(profile)
}

// getUserProfileWithCircuitBreaker fetches the user profile, wrapped with a circuit breaker.
func getUserProfileWithCircuitBreaker(userID int) (*UserProfile, error) {
	//Define the function to be protected by the circuit breaker
	protectedFunc := func() (interface{}, error) {
		profile, err := fetchUserProfile(userID)
		if err != nil {
			return nil, err
		}
		return profile, nil
	}

	//Execute the function through the circuit breaker
	result, err := cb.Execute(protectedFunc)
	if err != nil {
		//Circuit breaker is open or the request failed.
		return nil, fmt.Errorf("circuit breaker error: %w", err)
	}

	//Type assertion to convert the interface to a UserProfile
	profile, ok := result.(*UserProfile)
	if !ok {
		return nil, fmt.Errorf("unexpected type from circuit breaker")
	}
	return profile, nil

}

// fetchUserProfile simulates fetching the user profile from a User Service.
func fetchUserProfile(userID int) (*UserProfile, error) {
	resp, err := http.Get(fmt.Sprintf("%s/%d", userServiceURL, userID))
	if err != nil {
		return nil, fmt.Errorf("failed to call User Service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("User Service returned status: %d", resp.StatusCode)
	}

	var profile UserProfile
	if err := json.NewDecoder(resp.Body).Decode(&profile); err != nil {
		return nil, fmt.Errorf("failed to decode User Service response: %w", err)
	}

	return &profile, nil
}
```

**3. `user_service_simulator.go` - Simulating the User Service:**

This simulates a simple User Service, which will randomly return errors to test our circuit breaker.

```go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"time"

	"github.com/gorilla/mux"
)

// UserProfile represents the user profile data (same as in main.go).
type UserProfile struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

func main() {
	rand.Seed(time.Now().UnixNano()) // Seed the random number generator

	r := mux.NewRouter()
	r.HandleFunc("/user/{id}", getUserHandler).Methods("GET")

	log.Fatal(http.ListenAndServe(":8081", r)) // Run on port 8081
}

func getUserHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	userIDStr := vars["id"]
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		http.Error(w, "Invalid user ID", http.StatusBadRequest)
		return
	}

	// Simulate intermittent failures.  30% chance of failure.
	if rand.Intn(100) < 30 {
		http.Error(w, "Simulated User Service Error", http.StatusInternalServerError)
		return
	}

	profile := UserProfile{
		ID:    userID,
		Name:  fmt.Sprintf("User %d", userID),
		Email: fmt.Sprintf("user%d@example.com", userID),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(profile)
}
```

**4. Running the Services:**

Open two terminals. In one, run the User Service simulator:

```bash
go run user_service_simulator.go
```

In the other, run the main service:

```bash
go run main.go
```

**5. Testing the Circuit Breaker:**

Now, repeatedly call the `/profile/{id}` endpoint of your main service (e.g., `http://localhost:8080/profile/1`) using `curl` or a similar tool.  You should see that initially, the service returns user profiles successfully. However, after a few failures from the User Service simulator, the circuit breaker will open, and your main service will start returning errors related to the circuit breaker. After the timeout period, the circuit breaker will enter the half-open state and, if successful, will eventually close again.

## Common Mistakes
*   **Choosing the Wrong Thresholds:** Setting `MaxRequests`, `Interval`, `Timeout` and `ReadyToTrip` too low can lead to unnecessary tripping, while setting them too high can delay the circuit breaker from activating when needed. Monitor your system's performance and adjust these parameters accordingly.
*   **Not Implementing Fallbacks:**  When the circuit breaker is open, the service will fail.  It's crucial to provide a fallback mechanism (e.g., returning cached data, a default value, or a graceful error message) to maintain a good user experience.
*   **Ignoring Circuit Breaker State:** You can monitor the state of your circuit breaker (open, closed, half-open) to gain insights into the health of your downstream services.  Integrate this information into your monitoring dashboards.
*	**Using Global Variables:** The gobreaker library utilizes a global mutex for managing the state of the circuit breaker. While it's convenient, this can introduce contention in high-throughput applications. Consider using multiple circuit breakers or exploring alternative implementations for improved concurrency.
*	**Forgetting to Close Response Bodies:** Always remember to close the response body after making HTTP requests (`defer resp.Body.Close()`). Failing to do so can lead to resource leaks and eventually crash your application.

## Interview Perspective

Interviewers often assess your understanding of distributed systems and fault tolerance. When discussing circuit breakers, be prepared to explain:

*   The problem they solve (preventing cascading failures).
*   The states of a circuit breaker (closed, open, half-open).
*   How they relate to other resilience patterns (retries, timeouts).
*   How to choose appropriate thresholds and configurations.
*   The importance of fallbacks.
*   Specific implementations and libraries you've used (e.g., `gobreaker` in Go).

Key talking points include explaining the tradeoffs involved in configuring a circuit breaker and describing how you would monitor its effectiveness in a production environment.

## Real-World Use Cases

*   **E-commerce:**  Protecting the checkout service from failures in the payment processing service.
*   **Social Media:** Isolating the user feed service from problems in the recommendation engine.
*   **Financial Services:** Ensuring the core banking service remains available even if the reporting service is down.
*   **Content Delivery Networks (CDNs):**  Routing traffic away from failing origin servers to healthy ones.

In each of these scenarios, the circuit breaker helps to maintain the availability and responsiveness of critical services.

## Conclusion
Circuit breakers are an essential tool for building resilient microservices.  By preventing cascading failures and providing fallback mechanisms, they ensure that your system can gracefully handle errors and maintain a good user experience, even when dependent services are experiencing problems.  By understanding the core concepts and practical implementation, you can significantly improve the reliability of your distributed systems. Remember to carefully choose the right thresholds, implement robust fallbacks, and monitor the state of your circuit breakers to ensure their effectiveness.