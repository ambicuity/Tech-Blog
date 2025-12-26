---
title: "Building a Resilient API Gateway with Kong and Docker"
date: 2023-10-27 14:30:00 +0000
categories: [DevOps, Microservices]
tags: [api-gateway, kong, docker, microservices, resilience, reverse-proxy]
---

## Introduction

In the world of microservices, managing and securing API access is crucial. An API gateway acts as a single entry point for all client requests, routing them to the appropriate backend services. This simplifies client interactions, enhances security, and enables functionalities like rate limiting, authentication, and observability. Kong is a popular open-source API gateway built on top of Nginx and Lua. This post will guide you through building a resilient API gateway using Kong and Docker, enabling a robust and scalable solution for your microservices architecture.

## Core Concepts

Before diving into the implementation, let's define some key terms:

*   **API Gateway:** A reverse proxy that sits in front of one or more backend services (often microservices) and acts as a single point of entry. It handles authentication, authorization, rate limiting, request transformation, and other cross-cutting concerns.

*   **Kong:** An open-source, lightweight, and extensible API Gateway. It uses Nginx as its core and Lua for its plugin system. Kong exposes a RESTful Admin API for configuration.

*   **Docker:** A platform for building, running, and managing applications in isolated containers. Docker simplifies deployment and ensures consistency across different environments.

*   **Reverse Proxy:** A server that sits in front of one or more backend servers and forwards client requests to those servers. The reverse proxy hides the internal architecture of the backend from the client.

*   **Service Discovery:** A mechanism that allows services to automatically discover each other's network locations (IP address and port).

*   **Upstream:** In Kong terminology, an upstream represents the backend service that Kong will proxy requests to.

*   **Service:** In Kong, a service represents an abstract entity of a backend API or microservice.

*   **Route:** In Kong, a route defines how client requests are matched and forwarded to a specific service.

## Practical Implementation

We will use Docker Compose to orchestrate our Kong setup along with a sample "mockbin" service as our upstream. This implementation focuses on setting up Kong and routing requests to a simple backend.  For a more production-ready setup, consider adding a database (PostgreSQL or Cassandra) for Kong configuration.

**1. Create a `docker-compose.yml` file:**

```yaml
version: '3.8'

services:
  kong:
    image: kong:latest
    container_name: kong
    ports:
      - "8000:8000"   # Proxy port (HTTP)
      - "8443:8443"   # Proxy port (HTTPS)
      - "8001:8001"   # Admin API port (HTTP)
      - "8444:8444"   # Admin API port (HTTPS)
    environment:
      KONG_DATABASE: "off" # Use in-memory database for simplicity - NOT for production
      KONG_ADMIN_API_URI: "http://0.0.0.0:8001"
      KONG_PROXY_LISTEN: "0.0.0.0:8000, 0.0.0.0:8443 ssl" # Listen on all interfaces
      KONG_ADMIN_LISTEN: "0.0.0.0:8001, 0.0.0.0:8444 ssl" # Listen on all interfaces
    depends_on:
      - mockbin

  mockbin:
    image: mockbin/mockbin
    container_name: mockbin
    ports:
      - "8080:8080"

networks:
  default:
    name: kong-net
```

This `docker-compose.yml` file defines two services: `kong` and `mockbin`. Kong is configured to use an in-memory database (for simplicity - not suitable for production), and the necessary ports are exposed. Mockbin is used as our backend service. A network is also defined for communication between services.

**2. Start the services:**

```bash
docker-compose up -d
```

This command starts the Kong and Mockbin containers in detached mode.

**3. Configure Kong:**

Now, let's use the Kong Admin API to configure a service and a route.

First, create a service in Kong:

```bash
curl -i -X POST \
  --url http://localhost:8001/services \
  --data "name=mockbin-service" \
  --data "url=http://mockbin:8080"
```

This command creates a service named `mockbin-service` that points to the Mockbin service. We are using `mockbin` as the hostname because Docker Compose automatically resolves service names within the defined network.

Next, create a route for the service:

```bash
curl -i -X POST \
  --url http://localhost:8001/services/mockbin-service/routes \
  --data "name=mockbin-route" \
  --data "paths[]=/mockbin"
```

This command creates a route named `mockbin-route` that matches requests with the path `/mockbin` and routes them to the `mockbin-service`.

**4. Test the API Gateway:**

Now you can access the Mockbin service through Kong:

```bash
curl http://localhost:8000/mockbin
```

You should see the response from the Mockbin service. Kong is now acting as an API gateway, routing requests to your backend service.

**Resilience and Load Balancing:**

Kong offers various mechanisms to enhance resilience and load balancing. Let's explore a simple example of adding another mockbin instance.

**1. Scale Mockbin:**

Update your `docker-compose.yml` to include a second mockbin instance.  You'll also need to define health checks.

```yaml
version: '3.8'

services:
  kong:
    image: kong:latest
    container_name: kong
    ports:
      - "8000:8000"   # Proxy port (HTTP)
      - "8443:8443"   # Proxy port (HTTPS)
      - "8001:8001"   # Admin API port (HTTP)
      - "8444:8444"   # Admin API port (HTTPS)
    environment:
      KONG_DATABASE: "off" # Use in-memory database for simplicity - NOT for production
      KONG_ADMIN_API_URI: "http://0.0.0.0:8001"
      KONG_PROXY_LISTEN: "0.0.0.0:8000, 0.0.0.0:8443 ssl" # Listen on all interfaces
      KONG_ADMIN_LISTEN: "0.0.0.0:8001, 0.0.0.0:8444 ssl" # Listen on all interfaces
    depends_on:
      - mockbin1
      - mockbin2

  mockbin1:
    image: mockbin/mockbin
    container_name: mockbin1
    ports:
      - "8081:8080"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080"]
      interval: 10s
      timeout: 5s
      retries: 3

  mockbin2:
    image: mockbin/mockbin
    container_name: mockbin2
    ports:
      - "8082:8080"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080"]
      interval: 10s
      timeout: 5s
      retries: 3

networks:
  default:
    name: kong-net
```

Now scale the applications:

```bash
docker-compose down && docker-compose up -d
```

**2. Update Kong Upstream:**

Instead of pointing directly to `mockbin:8080`, we will create an upstream and target the individual instances. Delete the existing service:

```bash
curl -i -X DELETE http://localhost:8001/services/mockbin-service
```

Create an upstream:

```bash
curl -i -X POST http://localhost:8001/upstreams \
    --data "name=mockbin-upstream"
```

Add targets to the upstream:

```bash
curl -i -X POST http://localhost:8001/upstreams/mockbin-upstream/targets \
    --data "target=mockbin1:8080"
```

```bash
curl -i -X POST http://localhost:8001/upstreams/mockbin-upstream/targets \
    --data "target=mockbin2:8080"
```

Now, create a service pointing to the upstream:

```bash
curl -i -X POST \
  --url http://localhost:8001/services \
  --data "name=mockbin-service" \
  --data "url=http://mockbin-upstream"
```

Finally, recreate the route:

```bash
curl -i -X POST \
  --url http://localhost:8001/services/mockbin-service/routes \
  --data "name=mockbin-route" \
  --data "paths[]=/mockbin"
```

Kong will now load balance requests between the two Mockbin instances. If one instance fails (as detected by the health checks), Kong will automatically route traffic to the healthy instance.

## Common Mistakes

*   **Using the in-memory database in production:**  The in-memory database is suitable for development and testing but will lose all configuration data when the Kong container restarts. Use PostgreSQL or Cassandra for production deployments.
*   **Exposing the Admin API:**  The Admin API should be protected behind authentication and authorization to prevent unauthorized access.  Consider using Kong's built-in authentication plugins or a dedicated authentication service.  In production, it should *never* be exposed publicly.
*   **Ignoring health checks:**  Properly configured health checks are crucial for ensuring that Kong only routes traffic to healthy backend services.  Configure health checks both in your Docker Compose setup and within Kong (using the health check plugin).
*   **Not configuring request timeouts:** Without proper timeout configuration, Kong can hold onto connections indefinitely if a backend service becomes unresponsive, potentially leading to resource exhaustion.
*   **Lack of rate limiting:** Failing to implement rate limiting exposes your backend services to potential abuse and denial-of-service attacks. Use Kong's rate limiting plugin to protect your services.

## Interview Perspective

When discussing Kong in interviews, be prepared to answer questions about:

*   **The role of an API gateway:**  Explain the benefits of using an API gateway in a microservices architecture.
*   **Kong's architecture:**  Understand that Kong is built on top of Nginx and uses Lua for its plugin system.
*   **Kong's features:**  Be familiar with Kong's core features, such as authentication, authorization, rate limiting, traffic management, and observability.
*   **Kong's deployment options:**  Know how to deploy Kong using Docker, Kubernetes, and other platforms.
*   **Resilience and scalability:**  Discuss how Kong can be used to improve the resilience and scalability of your API infrastructure.
*   **The trade-offs of using Kong:** Be aware of the potential complexities of managing and configuring Kong, and the performance overhead introduced by the gateway.

Key talking points:

*   "Kong provides a centralized point for managing API traffic, simplifying client interactions and improving security."
*   "Kong's plugin system allows for easy extension of its functionality."
*   "Kong's open-source nature and large community make it a popular choice for API gateway solutions."
*   "We use Kong to implement rate limiting, authentication, and request transformation, ensuring the security and reliability of our microservices."

## Real-World Use Cases

*   **Microservices architectures:** Kong is commonly used to manage and secure access to microservices, providing a single entry point for client applications.
*   **Legacy API modernization:** Kong can be used to expose legacy APIs through a modern API gateway, enabling easier integration with new applications.
*   **Mobile application backends:** Kong can be used to manage and optimize API traffic for mobile applications, improving performance and reducing battery consumption.
*   **IoT platforms:** Kong can be used to manage and secure access to IoT devices, providing a scalable and reliable platform for data collection and control.
*   **Securing internal APIs:** Kong can be used to secure internal APIs, enforcing authentication and authorization policies.

## Conclusion

Building a resilient API gateway with Kong and Docker is essential for managing and securing API access in microservices architectures. By following the steps outlined in this post, you can set up a robust and scalable solution that enhances the performance, security, and observability of your applications. Remember to consider production-grade configurations for the database, health checks, and security. This setup provides a strong foundation for building more complex and resilient microservices-based systems.
