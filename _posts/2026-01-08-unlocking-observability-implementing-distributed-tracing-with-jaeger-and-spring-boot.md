---
layout: post
title: "Unlocking Observability: Implementing Distributed Tracing with Jaeger and Spring Boot"
date: 2026-01-08 21:08:13 +0000
categories: [DevOps, Microservices]
tags: [distributed-tracing, jaeger, spring-boot, observability, microservice-architecture]
---

## Introduction

In the world of microservices, where applications are composed of many independent services, debugging and understanding the flow of requests can be a nightmare. Traditional logging often falls short when tracing a request across multiple services. This is where distributed tracing comes in. This blog post will guide you through implementing distributed tracing using Jaeger, a popular open-source tracing system, and Spring Boot, a widely used Java framework for building microservices. We'll cover the core concepts, practical implementation steps, common pitfalls, and discuss its relevance in interviews and real-world scenarios.

## Core Concepts

Before diving into the implementation, let's understand the fundamental concepts of distributed tracing:

*   **Trace:** Represents the end-to-end journey of a request through a system. It's a collection of spans.
*   **Span:** Represents a single unit of work within a trace. Think of it as a timed operation. Each span has a start and end time, representing the duration of the operation. It also contains metadata, such as tags (key-value pairs) and logs.
*   **Span Context:** Contains information needed to propagate the trace across services. This includes the trace ID, span ID, and any baggage items. It's typically passed as HTTP headers.
*   **Trace ID:** A unique identifier for a trace, shared by all spans within that trace.
*   **Span ID:** A unique identifier for a span.
*   **Baggage:** Key-value pairs that are propagated along with the span context. Useful for carrying context information that is not directly related to tracing but relevant to the application's logic.
*   **Instrumentation:** The process of adding code to your application to create and report spans. This can be done manually or using automatic instrumentation libraries.
*   **Jaeger Agent:** A process that receives spans from your application and forwards them to the Jaeger Collector.
*   **Jaeger Collector:** Receives traces from the Jaeger Agent, validates them, and stores them in the storage backend.
*   **Jaeger Query:** The UI component that allows you to search for and visualize traces.
*   **Sampling:** A technique to reduce the amount of trace data collected. Not all requests need to be traced, especially in high-traffic systems.

## Practical Implementation

We'll create two simple Spring Boot microservices: `Service A` and `Service B`.  `Service A` will call `Service B`.  We'll then instrument both services to send trace data to Jaeger.

**Prerequisites:**

*   Java 11 or later
*   Maven or Gradle
*   Docker (for running Jaeger)

**Step 1: Start Jaeger using Docker**

The easiest way to get started with Jaeger is to use Docker.  Run the following command:

```bash
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 14268:14268 \
  jaegertracing/all-in-one:latest
```

This will start a Jaeger All-in-One container, which includes the Jaeger Agent, Collector, Query, and storage backend (in-memory). You can access the Jaeger UI at `http://localhost:16686`.

**Step 2: Create Service A (Spring Boot Application)**

Create a new Spring Boot project named `service-a`. Add the following dependencies to your `pom.xml` (if using Maven):

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>io.opentracing.contrib</groupId>
        <artifactId>opentracing-spring-jaeger-cloud-starter</artifactId>
        <version>3.3.1</version>
    </dependency>
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-openfeign</artifactId>
        <version>4.0.4</version>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-aop</artifactId>
    </dependency>
</dependencies>

<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.cloud</groupId>
      <artifactId>spring-cloud-dependencies</artifactId>
      <version>2022.0.4</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

Create a simple controller:

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ServiceAController {

    @Autowired
    private ServiceBClient serviceBClient;

    @GetMapping("/call-service-b")
    public String callServiceB() {
        return "Service A calling Service B: " + serviceBClient.getMessage();
    }
}
```

Create a Feign client to call Service B:

```java
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;

@FeignClient(name = "service-b", url = "http://localhost:8081") // Service B URL
public interface ServiceBClient {

    @GetMapping("/message")
    String getMessage();
}
```

Enable Feign clients in your Spring Boot application:

```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
@EnableFeignClients
public class ServiceAApplication {

    public static void main(String[] args) {
        SpringApplication.run(ServiceAApplication.class, args);
    }

}
```

Add the following configuration to `application.properties`:

```properties
spring.application.name=service-a
server.port=8080
```

**Step 3: Create Service B (Spring Boot Application)**

Create a new Spring Boot project named `service-b`. Add the same dependencies as Service A (except the Feign dependency).

Create a simple controller:

```java
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ServiceBController {

    @GetMapping("/message")
    public String getMessage() {
        return "Hello from Service B!";
    }
}
```

Add the following configuration to `application.properties`:

```properties
spring.application.name=service-b
server.port=8081
```

**Step 4: Run both services**

Run both `service-a` and `service-b` Spring Boot applications.

**Step 5: Test and Observe in Jaeger**

Access `http://localhost:8080/call-service-b` in your browser. This will trigger a call from Service A to Service B. Now, open the Jaeger UI at `http://localhost:16686`.

*   Select "service-a" from the "Service" dropdown.
*   Click "Find Traces".

You should see a trace that represents the call from Service A to Service B.  Click on the trace to see the spans, which will show the individual operations performed in each service. You'll see spans for the `GET /call-service-b` request in Service A and the `GET /message` request in Service B.

**Explanation:**

The `opentracing-spring-jaeger-cloud-starter` dependency automatically instruments your Spring Boot application.  It uses interceptors and filters to create spans for incoming requests and outgoing calls (using Feign). The starter configures a `JaegerTracer` which is responsible for sending the trace data to the Jaeger Agent. By default, it connects to `localhost:6831`, which is the default address of the Jaeger Agent running in the Docker container.

## Common Mistakes

*   **Forgetting to add the necessary dependencies:** Missing the `opentracing-spring-jaeger-cloud-starter` dependency will prevent automatic instrumentation. Ensure the Feign dependency is also included if using Feign clients.
*   **Incorrect Jaeger Agent configuration:** If the Jaeger Agent is running on a different host or port, you need to configure the `jaeger.reporter.host` and `jaeger.reporter.port` properties in your `application.properties` file.
*   **Not propagating the span context:** When making calls between services, it's crucial to propagate the span context. Feign handles this automatically, but if you're using other HTTP clients, you'll need to manually add the trace ID and span ID to the HTTP headers.
*   **Sampling configuration:**  By default, Jaeger often uses a probabilistic sampler that traces only a small percentage of requests. For development and testing, consider configuring a sampler that traces all requests.  You can do this using the `jaeger.sampler.type` and `jaeger.sampler.param` properties in your `application.properties`.
*   **Ignoring Baggage:**  Baggage can be invaluable for carrying contextual information. Remember to properly manage and propagate baggage when needed.
*   **Over-tracing:** Tracing everything can generate a lot of data and impact performance. Choose carefully which operations to trace and use sampling effectively.

## Interview Perspective

Interviewers often ask about distributed tracing to assess your understanding of microservice architectures and observability. Key talking points include:

*   **The benefits of distributed tracing:** Explain how it helps with debugging, performance monitoring, and understanding the flow of requests in complex systems.
*   **The core concepts of distributed tracing:** Be able to define traces, spans, span contexts, trace IDs, and span IDs.
*   **How distributed tracing works:** Describe the process of instrumentation, span creation, span context propagation, and data collection.
*   **Your experience with distributed tracing tools:** Discuss your experience with Jaeger, Zipkin, or other tracing systems.
*   **Challenges of implementing distributed tracing:** Talk about the challenges of instrumentation, context propagation, and performance overhead.
*   **Strategies for handling large volumes of trace data:** Discuss sampling techniques and storage considerations.

Be prepared to discuss specific scenarios where you've used distributed tracing to solve real-world problems. Emphasize the importance of tracing for understanding and optimizing distributed systems.

## Real-World Use Cases

Distributed tracing is crucial in many real-world scenarios:

*   **Debugging performance issues:**  Identify bottlenecks and slow operations in a complex microservice architecture.
*   **Understanding user journeys:**  Track the path of a user request across multiple services to understand the user experience.
*   **Monitoring service dependencies:**  Visualize the dependencies between services and identify potential points of failure.
*   **Optimizing resource utilization:**  Identify services that are consuming excessive resources and optimize their performance.
*   **Implementing fault tolerance:** Understand the impact of service failures on other services and implement appropriate fault tolerance mechanisms.
*   **Security auditing:** Trace requests to identify potential security vulnerabilities.

## Conclusion

Distributed tracing is an essential tool for managing and understanding complex microservice architectures. By using Jaeger with Spring Boot, you can gain valuable insights into the behavior of your distributed systems, making it easier to debug performance issues, optimize resource utilization, and improve the overall reliability of your applications. Remember to configure your Jaeger Agent correctly, propagate the span context, and use sampling effectively to avoid performance overhead. Implementing distributed tracing early in your development process will save you time and effort in the long run.