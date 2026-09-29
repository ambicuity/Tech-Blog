---
layout: post
title: "Pod Topology Spread Constraints Explained"
date: 2024-02-29
categories: [Kubernetes, Reliability]
tags: [kubernetes, scheduling]
author: ritesh
---

## Introduction

Kubernetes excels at managing and orchestrating containerized applications. One of its powerful features is the ability to control how pods are distributed across your cluster's topology.  Pod Topology Spread Constraints offer a declarative way to specify these distribution preferences, ensuring high availability, fault tolerance, and optimized resource utilization.  This blog post delves into the core concepts of Pod Topology Spread Constraints, exploring how they work and demonstrating practical examples to help you effectively manage your Kubernetes deployments.  We will explore the problem they solve and provide hands-on illustrations of their implementation.

## Core Concepts: Why Spread Matters

Before diving into the specifics, let's understand why spreading pods across a topology is important. Imagine deploying multiple replicas of an application without any specific distribution strategy.  Kubernetes might inadvertently place all replicas on the same node.  If that node fails, your application experiences a complete outage. Similarly, concentrating all pods in a single availability zone can lead to problems if that zone encounters issues.

Pod Topology Spread Constraints mitigate these risks by allowing you to define rules that dictate how Kubernetes should distribute your pods across different *topologies*. A topology can represent anything from nodes to availability zones, regions, or even custom-defined attributes.  This is critical for resilience.

Here are some key concepts to understand:

*   **Topology Key:**  This is the label used to identify the topology domains you want to spread across. Common examples include `kubernetes.io/hostname` (for nodes), `topology.kubernetes.io/zone` (for availability zones), and `topology.kubernetes.io/region` (for regions). You can also define your own custom labels.

*   **MaxSkew:**  This is the core of the constraint. It specifies the maximum acceptable difference in the number of pods between the most and least populated topology domains.  For example, a `maxSkew` of 1 means the difference in the number of matching pods in any two topology domains must be no more than 1.

*   **WhenUnsatisfiable:** This defines what Kubernetes should do when the constraint cannot be satisfied.  There are two options:

    *   `DoNotSchedule`: Kubernetes will not schedule the pod if the constraint cannot be met. This prioritizes strict adherence to the spreading strategy.
    *   `ScheduleAnyway`: Kubernetes will schedule the pod even if the constraint is violated. This prioritizes availability over strict adherence to the spreading strategy. This is useful when having some pods running is more important than adhering perfectly to the distribution rule.

*   **Label Selector:** This specifies which pods are subject to the constraint.  Typically, this will match the labels of the pods you're deploying.

*   **Namespaces:** Constraints can be applied cluster-wide or limited to a specific namespace. The example below focuses on deployment manifests within a single namespace.

## Implementation: Practical Examples

Let's illustrate how to use Pod Topology Spread Constraints with some practical examples.  We'll start with a simple deployment and gradually add constraints to improve its resilience.

**Scenario 1: Basic Deployment (No Constraints)**

First, let's define a basic deployment without any topology spread constraints:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
```

If you apply this deployment, Kubernetes will schedule the three replicas wherever it finds available resources. There's no guarantee they'll be spread across different nodes or availability zones.  This is the default, simplest scenario, but also the least resilient.

**Scenario 2: Spreading Across Nodes**

Now, let's add a Pod Topology Spread Constraint to ensure the pods are spread across different nodes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: my-app
```

In this example:

*   `maxSkew: 1` means the difference in the number of `my-app` pods on any two nodes should be at most 1.
*   `topologyKey: kubernetes.io/hostname` specifies that we want to spread across nodes (identified by their hostname).
*   `whenUnsatisfiable: DoNotSchedule` tells Kubernetes to not schedule the pod if the constraint cannot be met.

If you have only two nodes and this deployment is applied, two pods will be on one node and one pod on the other. If you only have one node, no pods will be scheduled.

**Scenario 3: Spreading Across Availability Zones**

To spread pods across availability zones, we can modify the `topologyKey`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: my-app
```

This configuration assumes your nodes are labeled with `topology.kubernetes.io/zone`. If you're using a cloud provider, this label is usually automatically applied. If you are running a bare metal cluster, you may have to apply these labels to the nodes yourself.

**Scenario 4: Relaxing Constraints with `ScheduleAnyway`**

Sometimes, strict adherence to the constraint might prevent pods from being scheduled, especially during resource shortages.  In such cases, you can use `whenUnsatisfiable: ScheduleAnyway`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: my-app
```

With this configuration, Kubernetes will try to spread pods across nodes, but if it cannot satisfy the `maxSkew` constraint (e.g., due to insufficient nodes or resource constraints), it will still schedule the pod on any available node. This prioritizes availability over perfect distribution.

**Scenario 5: Multiple Constraints**

You can combine multiple topology spread constraints to achieve more granular control over pod distribution. For example, you might want to spread pods across both nodes and availability zones:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: my-app
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: my-app
```

In this case, Kubernetes will attempt to satisfy both constraints: spreading pods across nodes and availability zones.  The scheduler will attempt to satisfy all constraints, in order.

## Monitoring and Troubleshooting

After implementing topology spread constraints, it's essential to monitor your pods' distribution to ensure they're being scheduled as expected.

*   **`kubectl describe pod <pod-name>`:**  This command shows the events related to the pod, including scheduling decisions.  Look for events related to topology spread constraints to identify any issues.

*   **Kubernetes Dashboard:** The Kubernetes dashboard provides a visual representation of your cluster's resources and pod distribution.

*   **Metrics and Monitoring Tools:**  Use tools like Prometheus and Grafana to collect and visualize metrics related to pod distribution across different topology domains.

If you encounter issues, consider the following:

*   **Insufficient Resources:** Make sure you have enough resources (CPU, memory) on your nodes to accommodate the pods.
*   **Node Labels:** Verify that your nodes are correctly labeled with the topology keys you're using in your constraints.
*   **Conflicting Constraints:** If you have multiple constraints, ensure they don't conflict with each other.

## Conclusion

Pod Topology Spread Constraints provide a powerful and flexible way to control how pods are distributed across your Kubernetes cluster. By understanding the core concepts and utilizing the examples provided, you can effectively improve your application's availability, fault tolerance, and resource utilization. Experiment with different configurations and monitor your deployments to fine-tune your spreading strategy for optimal performance. This declarative approach enables you to offload scheduling complexity to Kubernetes, letting you focus on application development. Consider incorporating these constraints into your deployment manifests for robust, scalable applications.
