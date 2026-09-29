---
layout: post
title: "Rejecting Unsafe AI-Generated Kubernetes Manifests with OPA Gatekeeper"
date: 2026-03-23 10:04:27 +0000
categories: [AI, Security]
tags: [kubernetes, opa-gatekeeper, policy-enforcement, ai-assisted-development, devsecops, admission-controller]
---

The rapid adoption of AI-assisted development tools—like the latest iterations of GPT, Opus, and Gemini—has undeniably accelerated software delivery. This efficiency extends to infrastructure-as-code, with AI increasingly generating Kubernetes deployment manifests alongside application logic. However, this velocity often comes at the cost of operational rigor. We've observed a concerning trend where AI-generated manifests, while syntactically valid, frequently omit critical security and resource management configurations essential for production environments. Containers are often configured to run as root by default, and crucial resource `requests` and `limits` are missing, creating significant security vulnerabilities and contributing to cluster instability.

Relying on manual human review to catch these omissions across a rapidly growing codebase is simply not scalable. The volume of AI-generated artifacts quickly overwhelms human capacity, leading to gaps slipping into production. To address this, our platform engineering team implemented an automated policy enforcement mechanism using OPA Gatekeeper, ensuring that all Kubernetes manifests—regardless of their origin—adhere to our organizational standards before they ever touch a cluster.

Consider a typical AI-generated deployment manifest that might look something like this. It's functional, but operationally deficient:

```yaml
# deployment-ai-generated-unsafe.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: insecure-ai-app
  labels:
    app: insecure-ai-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: insecure-ai-app
  template:
    metadata:
      labels:
        app: insecure-ai-app
    spec:
      containers:
      - name: my-ai-service
        image: myregistry/my-ai-service:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: MY_ENV_VAR
          value: "ai-generated-value"
        # No securityContext, no resource limits/requests
```

This manifest, if deployed, would create a container running as root and without defined resource boundaries, making it a prime candidate for privilege escalation or resource exhaustion issues within the cluster.

### Implementing OPA Gatekeeper for Automated Enforcement

Our strategy involves deploying OPA Gatekeeper as a validating admission webhook in Kubernetes. This allows us to intercept API requests (like `kubectl apply -f ...`) and validate them against custom policies written in Rego. If a manifest violates a policy, the API request is rejected, preventing the unsafe configuration from ever being created.

First, install Gatekeeper to your cluster. While there are Helm charts, a direct `kubectl apply` using the provided manifest from the Gatekeeper project is often sufficient for initial setup:

```bash
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.13/deploy/gatekeeper.yaml
```

Wait for the Gatekeeper pods to be ready:

```bash
kubectl get pods -n gatekeeper-system
# Example Output (STATUS should be Running for all):
# NAME                                           READY   STATUS    RESTARTS   AGE
# gatekeeper-audit-7d4d7f5b8-abcde               1/1     Running   0          5m
# gatekeeper-controller-manager-f8b8d8c9-fghij   1/1     Running   0          5m
```

Next, we define our policy. We'll start with two crucial policies:
1.  **Enforce `runAsNonRoot: true`**: Containers must explicitly run as a non-root user.
2.  **Enforce Resource `requests` and `limits`**: All containers must declare CPU and memory requests and limits.

These policies are defined using `ConstraintTemplate` and `Constraint` resources. The `ConstraintTemplate` defines the Rego logic, and the `Constraint` applies that logic to specific resources.

#### Policy 1: Enforce `runAsNonRoot: true`

```yaml
# policy-run-as-non-root.yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8spsprunasonroot
  annotations:
    description: Requires containers to run with a non-root UID. Corresponds to the `runAsNonRoot` field in PodSecurityPolicy.
spec:
  crd:
    spec:
      names:
        kind: K8sPSPRunAsNonRoot
      validation:
        openAPIV3Schema:
          type: object
          properties:
            exemptImages:
              type: array
              description: >-
                Optional list of regular expressions of images to exempt from the `runAsNonRoot` requirement.
                For example, 'my-init-container' or 'my-app-*'.
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8spsprunasonroot

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not has_field(container.securityContext, "runAsNonRoot")
          msg := sprintf("Containers must not run as root. Found container %v in pod %v which does not set 'securityContext.runAsNonRoot' to true.", [container.name, input.review.object.metadata.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          container.securityContext.runAsNonRoot == false
          msg := sprintf("Containers must not run as root. Found container %v in pod %v with 'securityContext.runAsNonRoot' set to false.", [container.name, input.review.object.metadata.name])
        }

        # Helper function to check if a field exists
        has_field(object, field) = true {
          object[field]
        }
        has_field(object, field) = false {
          not object[field]
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPSPRunAsNonRoot
metadata:
  name: pod-must-run-as-non-root
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    exemptImages:
    # Example: exempt a specific image or pattern if needed
    # - "myregistry/privileged-tool:.*"
```

Apply this policy:

```bash
kubectl apply -f policy-run-as-non-root.yaml
```

Now, attempting to deploy the `insecure-ai-app` manifest will be rejected:

```bash
kubectl apply -f deployment-ai-generated-unsafe.yaml
# Expected Error:
# Error from server ([denied by pod-must-run-as-non-root] Containers must not run as root. Found container my-ai-service in pod insecure-ai-app which does not set 'securityContext.runAsNonRoot' to true.): error when creating "deployment-ai-generated-unsafe.yaml": admission webhook "validation.gatekeeper.sh" denied the request: [denied by pod-must-run-as-non-root] Containers must not run as root. Found container my-ai-service in pod insecure-ai-app which does not set 'securityContext.runAsNonRoot' to true.
```

This is precisely the outcome we want: a clear rejection and an actionable error message forcing correction.

#### Policy 2: Enforce Resource `requests` and `limits`

While the above policy addresses security, resource management is equally critical for cluster stability. Missing resource definitions can lead to noisy neighbor issues, over-provisioning, or unexpected evictions.

```yaml
# policy-resource-limits.yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredresourcerequirements
  annotations:
    description: >-
      Requires containers to have CPU and memory requests and limits set.
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredResourceRequirements
      validation:
        openAPIV3Schema:
          type: object
          properties:
            exemptImages:
              type: array
              description: >-
                Optional list of regular expressions of images to exempt from the resource requirement.
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredresourcerequirements

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.limits.cpu
          msg := sprintf("Container %v must have a CPU limit.", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.limits.memory
          msg := sprintf("Container %v must have a memory limit.", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.requests.cpu
          msg := sprintf("Container %v must have a CPU request.", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.requests.memory
          msg := sprintf("Container %v must have a memory request.", [container.name])
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredResourceRequirements
metadata:
  name: pod-must-have-resource-limits
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    exemptImages:
    # Example: exempt kube-system images or specific tools
    # - "k8s.gcr.io/.*"
```

Apply this policy:

```bash
kubectl apply -f policy-resource-limits.yaml
```

Now, the previous unsafe AI-generated manifest would be rejected by one or both of these policies. The exact error message depends on which policy fails first or how Gatekeeper aggregates messages.

To successfully deploy, the AI (or developer) must generate a manifest that adheres to these policies:

```yaml
# deployment-ai-generated-safe.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-ai-app
  labels:
    app: secure-ai-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: secure-ai-app
  template:
    metadata:
      labels:
        app: secure-ai-app
    spec:
      containers:
      - name: my-ai-service
        image: myregistry/my-ai-service:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: MY_ENV_VAR
          value: "ai-generated-value"
        securityContext:
          runAsNonRoot: true # Enforced by policy
          runAsUser: 1000    # Good practice, runs as user 1000
          readOnlyRootFilesystem: true # Also good practice for hardening
        resources:           # Enforced by policy
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

With the corrected manifest, deployment proceeds successfully:

```bash
kubectl apply -f deployment-ai-generated-safe.yaml
# Expected output:
# deployment.apps/secure-ai-app created
```

This approach shifts the burden of operational correctness from manual post-facto review to automated pre-deployment validation. It establishes a necessary guardrail for AI-assisted software engineering, ensuring that increased development velocity does not compromise the security and stability of our production Kubernetes environments. By providing immediate feedback through admission control, we effectively train developers and implicitly, the AI models they use, to generate more robust and compliant infrastructure artifacts from the outset. This is how we scale human expertise in an AI-amplified world.
