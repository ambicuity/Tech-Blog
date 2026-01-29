yaml
---
layout: post
title: "Autoscaling: HPA and VPA Explained"
date: 2024-01-26
categories: [Tech, Engineering]
tags: [tech, software, engineering, kubernetes, autoscaling, hpa, vpa]
author: ritesh
---

## Introduction

In today's cloud-native world, applications need to be resilient and capable of handling varying workloads. Autoscaling is a critical component in achieving this, allowing applications to automatically adjust their resource allocation based on demand. Kubernetes offers two primary autoscaling mechanisms: Horizontal Pod Autoscaler (HPA) and Vertical Pod Autoscaler (VPA). While both aim to optimize resource utilization, they operate in fundamentally different ways. This post will delve into the core concepts, implementation details, and differences between HPA and VPA, providing practical examples to help you understand and leverage these powerful tools.

## Core Concepts: Horizontal vs. Vertical Scaling

Before diving into the specifics of HPA and VPA, it's important to understand the distinction between horizontal and vertical scaling.

*   **Horizontal Scaling (Scaling Out):** Involves adding more instances (pods in Kubernetes) of your application. This increases the overall capacity to handle more traffic or workload. The existing instances remain the same, but the number of instances grows or shrinks based on demand. HPA is responsible for horizontal scaling.

*   **Vertical Scaling (Scaling Up):** Involves increasing the resources (CPU, memory) allocated to an existing instance (pod). The number of instances remains constant, but each instance becomes more powerful. VPA is responsible for vertical scaling.

The choice between horizontal and vertical scaling depends on the application's architecture and resource constraints.  Generally, horizontal scaling is preferred for stateless applications, as it's easier to distribute load across multiple instances. Vertical scaling might be suitable for stateful applications or when adding more instances becomes impractical due to architectural limitations or licensing costs.

## Horizontal Pod Autoscaler (HPA)

The Horizontal Pod Autoscaler (HPA) automatically scales the number of pods in a replication controller, deployment, replica set, or stateful set based on observed CPU utilization, memory consumption, or custom metrics.  The HPA operates by monitoring the target metrics and adjusting the number of replicas to maintain the desired average utilization.

**How HPA Works:**

1.  **Metrics Collection:** The HPA uses the Kubernetes Metrics Server (or custom metrics adapters) to collect resource utilization data from the pods.  The Metrics Server aggregates resource metrics from Kubelets running on each node.

2.  **Evaluation:** The HPA controller periodically queries the Metrics Server (or custom metrics adapters) to retrieve the current resource utilization. It then compares these values against the target utilization specified in the HPA configuration.

3.  **Scaling Decision:** Based on the comparison, the HPA controller calculates the desired number of replicas. If the current utilization is higher than the target, the HPA increases the number of replicas. If the utilization is lower, it decreases the number of replicas.  The HPA respects minimum and maximum replica limits.

4.  **Scaling Action:** The HPA updates the `replicas` field in the target resource (e.g., Deployment). The Deployment controller then creates or deletes pods to match the desired number of replicas.

**Example: Deploying an HPA based on CPU utilization**

First, deploy a sample application (e.g., `nginx`):

yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 256Mi


Save this as `nginx-deployment.yaml` and apply it:

bash
kubectl apply -f nginx-deployment.yaml


Next, create an HPA that targets the `nginx-deployment` and scales based on CPU utilization:

yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50


Save this as `nginx-hpa.yaml` and apply it:

bash
kubectl apply -f nginx-hpa.yaml


This HPA will maintain an average CPU utilization of 50% across all `nginx` pods. If the CPU utilization exceeds 50%, the HPA will increase the number of pods, up to a maximum of 10. If the CPU utilization falls below 50%, the HPA will decrease the number of pods, down to a minimum of 1.

**Verifying HPA:**

You can check the status of the HPA using `kubectl get hpa`:

bash
kubectl get hpa nginx-hpa


This command will show the current number of replicas, the target CPU utilization, and the actual CPU utilization.  You can generate load using a tool like `hey` or `wrk` to trigger the autoscaling.

## Vertical Pod Autoscaler (VPA)

The Vertical Pod Autoscaler (VPA) automatically adjusts the CPU and memory requests and limits for pods to optimize resource utilization and ensure pods have the right amount of resources. Unlike HPA, VPA focuses on vertical scaling by changing the resource configurations of individual pods.

**How VPA Works:**

1.  **Monitoring:** The VPA observes the resource usage of pods over time. It collects data on CPU and memory consumption.

2.  **Recommender:** The VPA Recommender analyzes the collected data and calculates optimal resource requests and limits for the pods. It takes into account the application's historical resource usage, performance characteristics, and available node capacity.

3.  **Update Modes:** The VPA can operate in different update modes:

    *   **Off:** VPA only provides recommendations. You must manually apply the changes.
    *   **Initial:** VPA assigns resource requests on pod creation. Once created, it doesn't modify resources further.
    *   **Auto:** VPA automatically updates the pod's resource requests and limits by evicting the pod and creating a new one with the updated configuration. This is the most automated mode, but it can cause temporary disruptions.
    *   **Recreate:** Similar to Auto, but it always recreates the pod, even if the resource requests haven't changed significantly.

4.  **Updater:** The VPA Updater component executes the scaling action by evicting pods (in `Auto` mode) and triggering the creation of new pods with the recommended resource settings.

**Example: Deploying a VPA in Auto mode**

First, ensure the VPA is installed in your Kubernetes cluster. Instructions can be found in the official Kubernetes documentation. Once installed, deploy the same `nginx-deployment` as before.

Next, create a VPA configuration:

yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: nginx-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  updatePolicy:
    updateMode: "Auto"


Save this as `nginx-vpa.yaml` and apply it:

bash
kubectl apply -f nginx-vpa.yaml


This VPA will automatically adjust the CPU and memory requests and limits for the `nginx` pods based on observed usage. When VPA determines that a pod needs more or fewer resources, it will evict the pod and create a new one with the updated resource configuration. The `updateMode: "Auto"` setting ensures that the changes are applied automatically.

**Verifying VPA:**

You can check the status of the VPA using `kubectl get vpa nginx-vpa -o yaml`:

bash
kubectl get vpa nginx-vpa -o yaml


This command will show the current recommendations generated by the VPA Recommender, as well as the history of applied resource configurations.  You can also examine the pod definitions using `kubectl describe pod <pod-name>` to see the resource requests and limits assigned by the VPA.

## HPA vs. VPA: Key Differences and Considerations

| Feature          | HPA                                      | VPA                                             |
| ---------------- | ---------------------------------------- | ----------------------------------------------- |
| Scaling Type     | Horizontal (number of pods)              | Vertical (CPU/Memory per pod)                    |
| Trigger          | Resource utilization, custom metrics      | Resource utilization                              |
| Implementation   | Adds or removes pods                    | Modifies pod resource requests and limits       |
| Update Mode      | Instantaneous (new pods are created)       | Can cause pod eviction (in Auto mode)           |
| Suitability      | Stateless applications                   | Stateful applications, resource optimization     |
| Complexity       | Simpler to configure                     | More complex, requires VPA installation          |
| Disruption       | Minimal (new pods are created)           | Can be disruptive (pod eviction)               |

**When to use HPA:**

*   You need to scale your application based on traffic load or other dynamic metrics.
*   Your application is stateless and can be easily scaled horizontally.
*   You want to avoid modifying the resource configurations of existing pods.

**When to use VPA:**

*   You want to optimize resource utilization and ensure pods have the right amount of resources.
*   Your application is stateful or cannot be easily scaled horizontally.
*   You are willing to accept potential disruptions caused by pod eviction (in `Auto` mode).
*   You have applications with unpredictable resource needs.

**Combining HPA and VPA:**

In some scenarios, it can be beneficial to combine HPA and VPA. For example, you can use VPA to optimize the resource requests and limits for your pods, and then use HPA to scale the number of pods based on traffic load. This can result in more efficient resource utilization and improved application performance.  However, combining them requires careful planning and monitoring to avoid conflicts and ensure that both autoscaling mechanisms are working effectively.  A common pattern is to use VPA in "Initial" mode to size pods correctly and then use HPA to scale horizontally based on those VPA-provided resource requests.

## Conclusion

HPA and VPA are powerful tools for autoscaling applications in Kubernetes. Understanding the differences between them and how they work is crucial for building resilient and efficient applications. HPA provides horizontal scaling based on metrics, while VPA focuses on vertical scaling by optimizing resource requests and limits. By carefully considering your application's architecture, resource constraints, and performance requirements, you can choose the appropriate autoscaling mechanism or combination of mechanisms to achieve optimal resource utilization and application performance. The examples provided should give you a solid starting point for implementing these tools in your own Kubernetes environment.
