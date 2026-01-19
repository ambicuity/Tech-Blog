```markdown
---
title: "Efficiently Managing Secrets in Kubernetes with Sealed Secrets"
date: 2024-11-12 01:24:56 +0000
categories: [DevOps, Kubernetes]
tags: [kubernetes, secrets-management, security, sealed-secrets, k8s, encryption]
---

## Introduction

Kubernetes Secrets are the standard way to manage sensitive information like passwords, API keys, and certificates in your cluster. However, by default, Secrets are stored unencrypted in etcd, the Kubernetes cluster's backing store. This poses a security risk, especially when committing manifests to version control systems like Git.  Sealed Secrets offer a solution by allowing you to encrypt your Secrets before committing them, ensuring they remain secure even if your Git repository is compromised. This blog post will guide you through the process of using Sealed Secrets to enhance the security of your Kubernetes deployments.

## Core Concepts

Before diving into the implementation, let's understand the core concepts behind Sealed Secrets:

*   **Kubernetes Secrets:** These are Kubernetes objects used to store sensitive information.  Think of them as key-value pairs where the values are sensitive (e.g., `database_password: mysecretpassword`). By default, Secrets are base64 encoded, which is *not* encryption.
*   **Encryption:** The process of encoding data to prevent unauthorized access.  Sealed Secrets use asymmetric encryption.
*   **Asymmetric Encryption:**  A cryptographic system using pairs of keys: a public key (for encryption) and a private key (for decryption). Anyone can encrypt data with the public key, but only the holder of the private key can decrypt it.
*   **Sealed Secrets Controller:**  A Kubernetes controller that runs in your cluster. It manages the decryption of Sealed Secrets using the private key it holds.  The controller creates standard Kubernetes Secrets from the decrypted Sealed Secrets.
*   **`kubeseal` CLI:**  A command-line tool used to encrypt Kubernetes Secrets using the public key of the Sealed Secrets controller. This tool runs locally on your machine and generates a `SealedSecret` custom resource.
*   **`SealedSecret` Custom Resource:** A Kubernetes Custom Resource Definition (CRD) that represents an encrypted Secret. This is the resource you commit to your Git repository.  The Sealed Secrets controller decrypts it in the cluster.

In essence, you encrypt your Secret using the cluster's public key, making it safe to store in version control. The Sealed Secrets controller, running in the cluster and possessing the corresponding private key, decrypts the `SealedSecret` and creates a standard Kubernetes Secret for use by your applications.

## Practical Implementation

Here's a step-by-step guide to implementing Sealed Secrets in your Kubernetes cluster:

**1. Install the `kubeseal` CLI:**

Download the latest version of `kubeseal` from the Sealed Secrets GitHub repository ([https://github.com/bitnami-labs/sealed-secrets](https://github.com/bitnami-labs/sealed-secrets)) according to your operating system.  For example, on macOS:

```bash
brew install kubeseal
```

Or using `go`:

```bash
go install github.com/bitnami-labs/sealed-secrets/cmd/kubeseal@latest
```

Ensure the `kubeseal` binary is in your system's PATH.

**2. Install the Sealed Secrets Controller in your Kubernetes cluster:**

The recommended way to install the controller is using Helm:

```bash
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm repo update
helm install sealed-secrets sealed-secrets/sealed-secrets --namespace kube-system
```

Verify that the controller is running correctly:

```bash
kubectl get pods -n kube-system | grep sealed-secrets
```

You should see a pod running the `sealed-secrets-controller`.

**3. Create a Kubernetes Secret:**

Create a standard Kubernetes Secret YAML file. For example, `my-secret.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secret
type: Opaque
data:
  database_password: $(echo -n "mysecretpassword" | base64)
  api_key: $(echo -n "myapikey123" | base64)
```

Important: Remember to base64 encode the secret values.  The `echo -n ... | base64` command does this for you.

**4. Encrypt the Secret using `kubeseal`:**

Use the `kubeseal` CLI to encrypt the Secret, creating a `SealedSecret` resource:

```bash
kubeseal --format yaml < my-secret.yaml > sealed-my-secret.yaml
```

By default, `kubeseal` connects to your current Kubernetes context to fetch the public key from the Sealed Secrets controller.

You can also specify the controller namespace and name explicitly using flags:

```bash
kubeseal --controller-namespace kube-system --controller-name sealed-secrets -f my-secret.yaml > sealed-my-secret.yaml
```

**5. Inspect the `SealedSecret` YAML:**

Open `sealed-my-secret.yaml`.  You'll see a new YAML file containing a `SealedSecret` resource.  Notice that the `data` section contains encrypted values. This is the file you commit to your Git repository.  The original `my-secret.yaml` should *not* be committed.

**6. Apply the `SealedSecret` to your cluster:**

```bash
kubectl apply -f sealed-my-secret.yaml
```

**7. Verify the Secret:**

The Sealed Secrets controller will decrypt the `SealedSecret` and create a standard Kubernetes Secret named `my-app-secret` (as defined in the original `my-secret.yaml`). Verify this:

```bash
kubectl get secrets my-app-secret
kubectl get secrets my-app-secret -o yaml
```

You should see the Secret with the decrypted values. You can also decode the values by piping the base64 encoded data to `base64 -d`.

**8. Use the Secret in your application:**

Your applications can now access the decrypted Secret as they would with any standard Kubernetes Secret, using environment variables or volume mounts.

## Common Mistakes

*   **Committing unencrypted Secrets to Git:** This defeats the purpose of using Sealed Secrets. Ensure you only commit the `SealedSecret` YAML files, not the original Secret definitions.
*   **Incorrect Base64 Encoding:**  Ensure the secret values in your original Secret YAML are correctly base64 encoded.
*   **Controller Not Running:** Verify that the Sealed Secrets controller is running correctly and accessible in your cluster.  Check the logs for any errors.
*   **Mismatched Controller Name/Namespace:**  If you customized the controller's name or namespace during installation, ensure you specify the correct values when using `kubeseal`.
*   **Incorrect Context:** Make sure you are using the correct `kubectl` context when encrypting and applying the `SealedSecret`.

## Interview Perspective

Interviewers often ask about secrets management in Kubernetes, focusing on the security implications of storing Secrets unencrypted. Key talking points include:

*   **Understanding of Kubernetes Secrets and their limitations.**
*   **Knowledge of asymmetric encryption and how it's used in Sealed Secrets.**
*   **Ability to explain the workflow of encrypting and decrypting Secrets using Sealed Secrets.**
*   **Awareness of security best practices for secrets management.**
*   **Familiarity with other secrets management solutions like HashiCorp Vault.**
*   **Ability to describe the role of the `kubeseal` CLI and the Sealed Secrets controller.**

Be prepared to discuss the trade-offs between different secrets management approaches and the specific advantages of Sealed Secrets, especially its integration with GitOps workflows.  Understanding how the public/private key pair is managed is crucial.

## Real-World Use Cases

Sealed Secrets are particularly useful in scenarios where:

*   **You're using GitOps for managing your Kubernetes deployments.**  Sealed Secrets allow you to store your Secrets securely in your Git repositories.
*   **You're deploying applications to multiple Kubernetes clusters.**  You can use the same Sealed Secret across different clusters, as long as they're managed by the same Sealed Secrets controller (or have a compatible public/private key pair).
*   **You need a simple and lightweight solution for secrets management.**  Sealed Secrets are relatively easy to set up and use compared to more complex solutions like HashiCorp Vault.
*   **You want to avoid storing secrets in CI/CD pipelines.** You can store the sealed secrets in your repository and apply them during deployment.

## Conclusion

Sealed Secrets provide a practical and effective way to manage sensitive information securely in your Kubernetes cluster. By encrypting Secrets before committing them to version control, you can significantly reduce the risk of data breaches and improve the overall security posture of your deployments. While not a replacement for more comprehensive secrets management solutions like Vault, Sealed Secrets offer a valuable layer of security, especially in GitOps-driven environments. Remember to follow best practices, such as committing only the `SealedSecret` resources to your repository and ensuring your Sealed Secrets controller is properly configured.
```