```markdown
---
title: "Efficiently Managing Secrets in Kubernetes with Sealed Secrets"
date: 2023-10-27 14:30:00 +0000
categories: [DevOps, Kubernetes]
tags: [kubernetes, secrets-management, sealed-secrets, security, encryption, gitops]
---

## Introduction
Managing secrets in Kubernetes can be tricky. Storing them directly in YAML manifests is a major security risk, while using Kubernetes Secrets alone isn't ideal for GitOps workflows due to their base64 encoding.  This is where Sealed Secrets come into play. Sealed Secrets offer a safe and GitOps-friendly way to manage secrets by encrypting them so that only the Kubernetes controller running in your cluster can decrypt them. This allows you to safely store encrypted secrets in public repositories without compromising your application's security. This post will guide you through understanding and implementing Sealed Secrets for secure secret management in Kubernetes.

## Core Concepts
Before diving into the implementation, let's understand the core concepts:

*   **Kubernetes Secrets:** Kubernetes Secrets are objects that store sensitive information, such as passwords, OAuth tokens, and SSH keys. They can be mounted as files or environment variables into Pods. However, storing them in YAML manifests in plaintext is strongly discouraged.  While Kubernetes secrets are base64 encoded, this is *not* encryption. It's easily decoded.

*   **GitOps:** GitOps is a practice where infrastructure and application configurations are managed using Git repositories as the single source of truth. Changes are made through pull requests, providing auditability and version control. Managing Kubernetes resources through GitOps requires storing manifests in Git.

*   **Encryption:** The process of converting data into an unreadable format (ciphertext) that can only be decrypted with a specific key.

*   **Sealed Secrets:** A Kubernetes controller that allows you to encrypt Kubernetes Secrets into SealedSecrets, which can be safely stored in public repositories. Only the controller running within the cluster can decrypt them using a private key. The controller generates a key-pair for encryption/decryption when it is initially installed. The public key is used to encrypt the secret and the private key, only held by the SealedSecrets controller, is used to decrypt the secret.

*   **SealedSecret Controller:** This controller runs within your Kubernetes cluster and manages the decryption of SealedSecrets. It holds the private key required to decrypt the encrypted data.

*   **kubeseal:** A command-line tool used to encrypt Kubernetes Secrets using the SealedSecrets controller's public key. You use this to encrypt secrets locally (or in CI/CD) before pushing them to your Git repository.

## Practical Implementation
Here's a step-by-step guide to implementing Sealed Secrets in your Kubernetes cluster:

**1. Install the Sealed Secrets Controller:**

We will use Helm to install the Sealed Secrets controller. If you don't have Helm installed, you can follow the instructions on the Helm website: [https://helm.sh/docs/intro/install/](https://helm.sh/docs/intro/install/)

First, add the bitnami Helm repository:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

Now, install the Sealed Secrets controller:

```bash
helm install sealed-secrets bitnami/sealed-secrets --namespace kube-system
```

This command installs the Sealed Secrets controller in the `kube-system` namespace.  Verify the pod is running.

```bash
kubectl get pods -n kube-system | grep sealed-secrets
```

**2. Install `kubeseal` CLI Tool:**

Download the `kubeseal` CLI tool from the Sealed Secrets GitHub repository. The specific URL will vary depending on the latest version and your operating system. You can find the latest release at: [https://github.com/bitnami-labs/sealed-secrets/releases](https://github.com/bitnami-labs/sealed-secrets/releases). Look for pre-built binaries.

For example, on Linux (amd64):

```bash
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/kubeseal-linux-amd64
chmod +x kubeseal-linux-amd64
sudo mv kubeseal-linux-amd64 /usr/local/bin/kubeseal
kubeseal --version
```

**3. Create a Kubernetes Secret:**

Let's create a simple Kubernetes Secret containing sensitive information. Create a file named `my-secret.yaml` with the following content:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: $(echo -n "admin" | base64)
  password: $(echo -n "password123" | base64)
```

**Important:** The `data` field requires base64 encoded values.  Don't store plain text passwords here! This example uses a simple way to encode the password, but in a production environment, you should retrieve these values from a secure vault or use a more robust method of encoding.

**4. Encrypt the Secret with `kubeseal`:**

Now, use the `kubeseal` command to encrypt the Secret:

```bash
kubectl apply -f my-secret.yaml
kubeseal --format yaml --namespace default < my-secret.yaml > my-sealed-secret.yaml
```

This command does the following:

*   `kubectl apply -f my-secret.yaml`: Applies the Kubernetes Secret to your cluster (temporarily).  This is only so `kubeseal` can get the Secret data to encrypt.
*   `kubeseal --format yaml --namespace default < my-secret.yaml > my-sealed-secret.yaml`: Encrypts the Secret using the Sealed Secrets controller's public key and saves the output to `my-sealed-secret.yaml`. It's crucial to specify the correct namespace where your Secret resides.

**5. Delete the Original Secret:**

After encrypting the secret, it is crucial to delete the plaintext secret that was created.

```bash
kubectl delete secret my-secret
```

**6. Inspect the SealedSecret Manifest:**

Open `my-sealed-secret.yaml`. You'll see a new manifest with the `kind: SealedSecret`. It will look something like this:

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  creationTimestamp: null
  name: my-secret
  namespace: default
spec:
  encryptedData:
    password: AgCT...
    username: AgCT...
  template:
    metadata:
      creationTimestamp: null
      name: my-secret
      namespace: default
    type: Opaque
```

Notice the `encryptedData` field.  This contains the encrypted values of your username and password. This entire file can be safely stored in your Git repository.

**7. Apply the SealedSecret to your cluster:**

```bash
kubectl apply -f my-sealed-secret.yaml
```

The Sealed Secrets controller will automatically decrypt the SealedSecret and create a regular Kubernetes Secret in the same namespace.

**8. Verify the Secret:**

```bash
kubectl get secrets my-secret -o yaml
```

You should see a Kubernetes Secret named `my-secret` with the decrypted data.

## Common Mistakes

*   **Forgetting to delete the original Secret:** This leaves the sensitive data exposed. Always delete the original Secret after encryption.
*   **Using the wrong namespace:** Ensure you specify the correct namespace when using `kubeseal`. If the namespace in the SealedSecret doesn't match the namespace where you want the Secret, the controller won't decrypt it.
*   **Committing the unencrypted Secret to Git:** This defeats the entire purpose of Sealed Secrets. Make sure you only commit the `SealedSecret` manifest.
*   **Incorrectly configured RBAC:** The SealedSecrets controller needs sufficient RBAC permissions to decrypt Secrets. Verify the service account associated with the controller has the necessary permissions.
*   **Using the same encryption key across multiple clusters:** Each Kubernetes cluster should have its own unique Sealed Secrets key pair. Sharing keys across clusters introduces a security risk. If you have a disaster and lose the Sealed Secrets controller's private key, you lose the ability to decrypt all secrets encrypted using that private key. This can mean rebuilding all your secrets. Back up the key!

## Interview Perspective

When discussing Sealed Secrets in an interview, be prepared to address the following:

*   **Problem Statement:** Clearly articulate the challenges of managing secrets in Kubernetes, especially in the context of GitOps.
*   **Sealed Secrets Solution:** Explain how Sealed Secrets addresses these challenges by providing a safe and GitOps-friendly way to store secrets.
*   **Encryption Process:** Describe the encryption process, highlighting the role of the `kubeseal` CLI tool and the Sealed Secrets controller.
*   **Security Considerations:** Discuss the security implications of using Sealed Secrets, including key management and best practices.
*   **Alternatives:** Be aware of alternative secret management solutions, such as HashiCorp Vault, and be prepared to compare and contrast them with Sealed Secrets. Discuss trade-offs.
*   **Operational Concerns:** Discuss the operational overhead associated with managing Sealed Secrets, including initial setup, key rotation, and troubleshooting.

Key talking points: encryption at rest, GitOps compatibility, key management, minimizing attack surface.

## Real-World Use Cases

*   **GitOps Workflows:** Store application configuration, including database credentials and API keys, in Git repositories without compromising security.
*   **Multi-Cluster Environments:** Deploy the same application configuration across multiple Kubernetes clusters, each with its own unique secrets.
*   **Open Source Projects:** Share application configuration with the community while keeping sensitive information private. This could be used for setting up a project locally.
*   **Continuous Integration/Continuous Deployment (CI/CD):** Securely manage secrets used in CI/CD pipelines, such as API tokens for deploying applications.

## Conclusion

Sealed Secrets provide a valuable solution for managing secrets in Kubernetes, especially in GitOps environments. By encrypting secrets before storing them in Git repositories, you can significantly improve the security of your application deployments. This post has provided a practical guide to implementing Sealed Secrets, including key concepts, step-by-step instructions, common mistakes, interview perspectives, and real-world use cases. By leveraging Sealed Secrets, you can streamline your secret management workflow and enhance the overall security of your Kubernetes deployments. Remember to always prioritize security best practices, such as proper key management and regular security audits.
```