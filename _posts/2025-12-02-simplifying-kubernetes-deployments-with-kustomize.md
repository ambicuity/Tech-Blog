---
title: "Simplifying Kubernetes Deployments with Kustomize"
date: 2025-12-02 13:00:51 +0000
categories: [DevOps, Kubernetes]
tags: [kubernetes, kustomize, deployments, configuration-management, declarative-configuration]
---

## Introduction
Managing Kubernetes deployments can become complex quickly, especially when dealing with multiple environments (development, staging, production). Traditionally, you might duplicate Kubernetes YAML manifests and manually modify them for each environment. Kustomize offers a better approach: a declarative configuration management tool built into `kubectl` that allows you to customize Kubernetes YAML files without actually modifying the original files. This simplifies deployments, reduces redundancy, and promotes consistency across environments. This blog post will guide you through using Kustomize to manage Kubernetes deployments effectively.

## Core Concepts

At its core, Kustomize works by applying patches to a base set of Kubernetes YAML files.  Think of it as a way to layer customizations on top of a common foundation.  This allows you to maintain a single source of truth for your base configurations and then apply environment-specific changes as needed.  Here are the key concepts:

*   **Base:** The base YAML files that define the core resources. This is often the most generic version of your deployment.
*   **Overlay:**  A set of customizations applied to the base.  Each environment (dev, staging, prod) usually has its own overlay.
*   **Kustomization:** A file named `kustomization.yaml` (or `kustomization.yml`) that defines the base and any overlays to be applied. This file acts as the entry point for Kustomize.
*   **Patch:** A YAML file containing changes to be applied to the base. These changes can include modifying resource properties (e.g., image tag, resource limits), adding new resources, or removing existing resources.

Kustomize works declaratively. You specify the desired state in your `kustomization.yaml` and Kustomize takes care of generating the final Kubernetes YAML. This is in contrast to imperative approaches where you directly modify the YAML files.

## Practical Implementation

Let's walk through a practical example of using Kustomize to manage a simple deployment.  We'll start with a base deployment and then create overlays for development and production environments.

**1. Create a Base Deployment:**

First, create a directory structure:

```bash
mkdir -p kustomize-example/base
cd kustomize-example/base
```

Now, create a `deployment.yaml` file:

```yaml
# kustomize-example/base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: nginx:latest
        ports:
        - containerPort: 80
```

Next, create a `service.yaml` file:

```yaml
# kustomize-example/base/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

Finally, create the `kustomization.yaml` in the `base` directory:

```yaml
# kustomize-example/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
```

**2. Create Overlays for Development and Production:**

Now, create directories for the `dev` and `prod` overlays:

```bash
mkdir -p ../overlays/dev
mkdir -p ../overlays/prod
```

**Development Overlay:**

Create a `kustomization.yaml` file in the `overlays/dev` directory:

```yaml
# kustomize-example/overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
  - ../../base

patches:
  - path: deployment-patch.yaml
    target:
      kind: Deployment
      name: my-app

namespace: dev
```

This `kustomization.yaml` specifies the `base` directory and a `patch` to be applied to the `Deployment`.  It also sets the namespace to `dev`.  Create the `deployment-patch.yaml` file in the `overlays/dev` directory:

```yaml
# kustomize-example/overlays/dev/deployment-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 2 # Increased replicas for development
  template:
    spec:
      containers:
      - name: my-app
        image: nginx:latest # Can use a different or more specific tag for dev
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
```

**Production Overlay:**

Create a `kustomization.yaml` file in the `overlays/prod` directory:

```yaml
# kustomize-example/overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
  - ../../base

patches:
  - path: deployment-patch.yaml
    target:
      kind: Deployment
      name: my-app

namespace: prod

images:
  - name: nginx
    newTag: "1.21.0" # Specify a stable nginx version for production
```

And the `deployment-patch.yaml`:

```yaml
# kustomize-example/overlays/prod/deployment-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3 # Increased replicas for production
  template:
    spec:
      containers:
      - name: my-app
        resources:
          limits:
            cpu: "1000m"
            memory: "1Gi"
```

**3. Apply the Configurations:**

To apply the configurations to your Kubernetes cluster, navigate to the desired overlay directory and run the following command:

```bash
kubectl apply -k .
```

For example, to apply the development configuration:

```bash
cd overlays/dev
kubectl apply -k . -n dev # Specify the namespace explicitly
```

Similarly, for production:

```bash
cd ../prod
kubectl apply -k . -n prod # Specify the namespace explicitly
```

**4. Generate the YAML (Optional):**

You can generate the final YAML files without applying them using the `kustomize build` command. This is useful for inspecting the generated configuration:

```bash
kustomize build . > output.yaml
```

## Common Mistakes

*   **Incorrect Patch Targeting:** Ensure your patches target the correct resources using the `target` field in your `kustomization.yaml`.  Mistargeted patches can lead to unexpected changes or failed deployments. Double-check `kind` and `name`.
*   **Overly Complex Patches:** Keep your patches small and focused.  Large, complex patches can be difficult to maintain and debug. Consider breaking them down into smaller, more manageable units.
*   **Misunderstanding Resource Merging:** Kustomize intelligently merges resources. Understand how fields are merged (e.g., lists are often appended, not replaced) to avoid unexpected behavior.  Sometimes, a strategic removal of an element is necessary.
*   **Ignoring Namespaces:** Remember to set the namespace in your overlays or use the `-n` flag with `kubectl apply` to ensure resources are deployed to the correct namespace.
*   **Not Using the `images` Transformer:** For image updates, using the `images` transformer in `kustomization.yaml` (like in the prod example) is preferable to patching the `image` field directly in the deployment manifest. It's more robust and easier to manage.
*   **Missing `kustomize build` Preview:** Before applying changes, ALWAYS use `kustomize build` and inspect the generated YAML. This helps catch errors early.

## Interview Perspective

When discussing Kustomize in interviews, be prepared to explain the following:

*   **What problem Kustomize solves:** Configuration management for Kubernetes deployments, especially across multiple environments.
*   **Key concepts:** Base, overlay, patch, kustomization.
*   **How Kustomize works:**  Applying patches to a base set of YAML files.
*   **Benefits of using Kustomize:** Reduced redundancy, improved consistency, easier management of environment-specific configurations, declarative approach.
*   **Alternatives to Kustomize:** Helm, Kubectl Apply with templating (e.g., `envsubst`), other configuration management tools.  Know the tradeoffs.
*   **Best practices:** Small, focused patches; thorough testing; using the `images` transformer.
*   **Experience using Kustomize:** Be prepared to describe specific projects where you used Kustomize and the benefits you observed. Describe challenges you faced and how you overcame them.

Key talking points:

*   "I've used Kustomize to manage deployments across development, staging, and production environments, significantly reducing configuration drift."
*   "I prefer Kustomize over Helm for simpler deployments where templating isn't necessary, as it avoids the complexity of Tiller and package management."
*   "I always use `kustomize build` to preview the generated YAML before applying changes to the cluster."

## Real-World Use Cases

*   **Managing Different Environments:** The primary use case is managing deployments across development, staging, and production environments. Kustomize allows you to easily customize configurations for each environment without duplicating the base YAML files.
*   **Feature Flagging:** You can use Kustomize to enable or disable features in different environments by applying patches that modify the deployment configuration.
*   **Resource Customization:** You can use Kustomize to customize resource requests and limits, image versions, and other deployment parameters based on the environment.
*   **Canary Deployments:** Create overlays for canary deployments with specific image tags and reduced replica counts to test new versions of your application.
*   **Microservices Architecture:** Use Kustomize to manage the configuration of multiple microservices, each with its own base deployment and environment-specific overlays.

## Conclusion

Kustomize provides a powerful and elegant way to manage Kubernetes deployments. By embracing its declarative approach and layering customizations on top of a common base, you can simplify your deployment workflows, reduce redundancy, and promote consistency across environments. Mastering Kustomize is an invaluable skill for any DevOps engineer or developer working with Kubernetes. Remember to keep your patches focused, test thoroughly, and always preview the generated YAML before applying changes to your cluster.