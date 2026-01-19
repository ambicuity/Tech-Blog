---
title: "Mastering Kubernetes Ingress: Routing Traffic to Your Services"
date: 2025-03-02 07:24:46 +0000
categories: [DevOps, Kubernetes]
tags: [kubernetes, ingress, nginx, routing, load-balancing, microservices]
---

## Introduction

Kubernetes Ingress is a powerful API object that manages external access to services within a Kubernetes cluster. Instead of exposing each service individually with a `NodePort` or `LoadBalancer` service type (which can become complex and expensive), Ingress acts as a smart traffic director, routing incoming requests to the correct backend services based on hostname, path, or other rules. This simplifies service exposure, reduces costs, and provides a centralized point for managing routing policies. This blog post will guide you through understanding and implementing Kubernetes Ingress, focusing on practical examples and common pitfalls.

## Core Concepts

Before diving into the implementation, let's define some key concepts:

*   **Service:** A Kubernetes Service is an abstraction that exposes an application running on a set of Pods as a network service. Services provide a stable IP address and DNS name for your applications.

*   **Ingress:**  An API object that manages external access to the services in a cluster, typically via HTTP.  It can provide load balancing, SSL termination, and name-based virtual hosting.

*   **Ingress Controller:**  A specialized load balancer that watches the Kubernetes API server for updates to Ingress resources. When an Ingress resource is created, updated, or deleted, the Ingress Controller automatically configures itself to reflect the desired routing rules.  Popular Ingress Controllers include Nginx, Traefik, and HAProxy.

*   **Ingress Resource:**  A Kubernetes manifest that defines the routing rules for your Ingress Controller. It specifies which hostnames and paths should be routed to which services.

*   **Name-based Virtual Hosting:**  The Ingress Controller can route traffic to different backend services based on the hostname requested in the HTTP header. This allows you to host multiple websites or applications on a single IP address.

*   **Path-based Routing:**  The Ingress Controller can route traffic to different backend services based on the path requested in the URL. This allows you to expose different parts of an application under different paths.

## Practical Implementation

Let's demonstrate how to set up a basic Ingress with the Nginx Ingress Controller. We'll assume you already have a Kubernetes cluster running and `kubectl` configured.

**Step 1: Install the Nginx Ingress Controller**

There are several ways to install the Nginx Ingress Controller.  A common approach is to use `kubectl apply` with a pre-defined manifest.  For example:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.4/deploy/static/provider/cloud/deploy.yaml
```

This command downloads and applies a manifest that deploys the Nginx Ingress Controller in your cluster.  Check the [official Kubernetes Ingress Nginx documentation](https://kubernetes.github.io/ingress-nginx/deploy/) for the latest version and installation instructions tailored to your environment (e.g., bare-metal, cloud provider).

**Step 2: Deploy Example Services**

Let's deploy two simple services named `service-a` and `service-b`. These services will simply echo their service name.

```yaml
# service-a.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: service-a
spec:
  selector:
    matchLabels:
      app: service-a
  replicas: 1
  template:
    metadata:
      labels:
        app: service-a
    spec:
      containers:
      - name: service-a
        image: kennethreitz/httpbin
        ports:
        - containerPort: 80

---
apiVersion: v1
kind: Service
metadata:
  name: service-a
spec:
  selector:
    app: service-a
  ports:
  - port: 80
    targetPort: 80
```

```yaml
# service-b.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: service-b
spec:
  selector:
    matchLabels:
      app: service-b
  replicas: 1
  template:
    metadata:
      labels:
        app: service-b
    spec:
      containers:
      - name: service-b
        image: kennethreitz/httpbin
        ports:
        - containerPort: 80

---
apiVersion: v1
kind: Service
metadata:
  name: service-b
spec:
  selector:
    app: service-b
  ports:
  - port: 80
    targetPort: 80
```

Apply these deployments and services:

```bash
kubectl apply -f service-a.yaml
kubectl apply -f service-b.yaml
```

**Step 3: Create the Ingress Resource**

Now, let's create an Ingress resource that routes requests to these services based on the hostname.  We'll route requests to `service-a.example.com` to the `service-a` service and requests to `service-b.example.com` to the `service-b` service.

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: service-a.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: service-a
            port:
              number: 80
  - host: service-b.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: service-b
            port:
              number: 80
```

*   `kubernetes.io/ingress.class: nginx`: This annotation tells Kubernetes to use the Nginx Ingress Controller for this Ingress resource.
*   `rules`: This section defines the routing rules.
*   `host`:  The hostname that the Ingress Controller should listen for.
*   `path`: The path that the Ingress Controller should match. `/` matches all paths.
*   `pathType: Prefix`: Specifies that the path is a prefix.  Alternatives include `Exact` and `ImplementationSpecific`.
*   `backend`:  Specifies the service and port to route traffic to.

Apply the Ingress resource:

```bash
kubectl apply -f ingress.yaml
```

**Step 4: Test the Ingress**

To test the Ingress, you need to resolve the hostnames `service-a.example.com` and `service-b.example.com` to the IP address of the Ingress Controller. The easiest way to do this is to add entries to your `/etc/hosts` file (or equivalent).

First, get the external IP address of the Ingress Controller:

```bash
kubectl get service ingress-nginx-controller -n ingress-nginx -o wide
```

Look for the `EXTERNAL-IP` column.  If it's `<pending>`, it means the Ingress Controller is still provisioning its external IP (common in cloud environments).  Wait until an IP address is assigned.

Then, add the following lines to your `/etc/hosts` file, replacing `<EXTERNAL_IP>` with the actual IP address:

```
<EXTERNAL_IP> service-a.example.com
<EXTERNAL_IP> service-b.example.com
```

Finally, test the Ingress using `curl`:

```bash
curl http://service-a.example.com
curl http://service-b.example.com
```

You should see output confirming that you reached `service-a` and `service-b` respectively.

## Common Mistakes

*   **Incorrect Ingress Class Annotation:**  Ensure the `kubernetes.io/ingress.class` annotation matches the name of your Ingress Controller. If it's missing or incorrect, the Ingress Controller won't process the resource.
*   **Service Port Mismatch:** Double-check that the `port.number` in the Ingress resource matches the `targetPort` in the Service definition. This is a common source of routing failures.
*   **DNS Resolution Issues:**  If you're using hostnames, ensure they resolve correctly to the Ingress Controller's IP address. Using incorrect DNS settings will prevent traffic from reaching your services.
*   **Missing Health Checks:**  Configure health checks (liveness and readiness probes) for your Pods. The Ingress Controller relies on these health checks to ensure it only routes traffic to healthy instances.
*   **Overlapping Paths:** If you have overlapping paths in your Ingress rules, the Ingress Controller will typically use the most specific path. Be mindful of the order of your rules.

## Interview Perspective

When discussing Kubernetes Ingress in an interview, be prepared to:

*   **Explain the benefits of using Ingress over `NodePort` or `LoadBalancer` services.** Highlight the cost savings, simplified routing, and centralized management.
*   **Describe the different types of Ingress Controllers available.**  Mention Nginx, Traefik, and HAProxy, and discuss their strengths and weaknesses.
*   **Explain how Ingress Controllers work.** Describe how they watch the Kubernetes API and dynamically configure themselves based on Ingress resources.
*   **Discuss common Ingress annotations.** Explain the purpose of annotations like `kubernetes.io/ingress.class`, and `nginx.ingress.kubernetes.io/rewrite-target`.
*   **Troubleshoot common Ingress issues.** Be prepared to discuss DNS resolution, service port mismatches, and incorrect Ingress class annotations.

Key talking points include scalability, security (SSL termination), and ease of management.

## Real-World Use Cases

*   **Exposing Microservices:** Ingress is commonly used to expose a suite of microservices under a single domain. Each microservice can be accessed via a different path or subdomain.
*   **Hosting Multiple Websites:** Ingress allows you to host multiple websites on a single Kubernetes cluster using name-based virtual hosting.
*   **API Gateway:** Ingress can act as an API gateway, providing a centralized point for routing API requests to different backend services, handling authentication, and enforcing rate limits.
*   **Blue/Green Deployments:** Ingress can be used to gradually shift traffic from an old version of an application to a new version during a blue/green deployment.
*   **Canary Releases:** Similar to blue/green deployments, Ingress can be used to route a small percentage of traffic to a canary release of an application for testing.

## Conclusion

Kubernetes Ingress is an essential tool for managing external access to services in a Kubernetes cluster. By understanding the core concepts, following the implementation steps, and avoiding common mistakes, you can effectively use Ingress to simplify service exposure, reduce costs, and improve the overall manageability of your Kubernetes deployments. Remember to choose an Ingress Controller that aligns with your specific needs and to continuously monitor and optimize your Ingress configurations to ensure optimal performance and security.