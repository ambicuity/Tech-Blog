```markdown
---
title: "Efficiently Managing Kubernetes Secrets with Sealed Secrets"
date: 2023-10-27 14:30:00 +0000
categories: [DevOps, Kubernetes]
tags: [kubernetes, secrets, sealed-secrets, security, gitops, encryption]
---

## Introduction

Managing secrets in Kubernetes can be tricky.  Storing sensitive information like API keys, passwords, and certificates directly in Kubernetes Secret objects exposes them to potential risks, especially when managing configurations with GitOps.  Unencrypted Secrets committed to Git repositories are a major security vulnerability.  Sealed Secrets provide a robust solution by allowing you to encrypt your Kubernetes Secrets so that they can be safely stored in public repositories. Only the controller running in your cluster can decrypt them. This blog post will guide you through the process of setting up and using Sealed Secrets to protect your sensitive data in Kubernetes.

## Core Concepts

Before diving into the implementation, let's cover some essential concepts:

*   **Kubernetes Secrets:**  Objects used to store sensitive information like passwords, OAuth tokens, and SSH keys. They can be consumed by pods via environment variables, volume mounts, or as files.  While Kubernetes offers built-in Secret management, the data is stored in base64 encoded format, which is easily decodable and not truly secure.

*   **GitOps:** A declarative approach to infrastructure and application management where the desired state of the system is defined in Git repositories.  Changes are deployed automatically based on pull requests, promoting auditability, reproducibility, and collaboration.  GitOps is incompatible with plain text secrets, because you can't store them in Git!

*   **Encryption at Rest:** Protecting data by encrypting it while it's stored on disk or in other persistent storage.  Sealed Secrets leverages encryption at rest to protect the sensitive data within the Kubernetes Secrets.

*   **Public-Key Cryptography (Asymmetric Encryption):** Sealed Secrets utilizes an asymmetric encryption scheme. A public key is used to encrypt the secret, and a corresponding private key is required for decryption. Only the controller, which has access to the private key, can decrypt the data.

*   **SealedSecrets Controller:**  A controller that runs in your Kubernetes cluster. It generates an RSA key pair, stores the private key securely within the cluster, and exposes the public key.  The controller is responsible for decrypting SealedSecret resources into standard Kubernetes Secret objects.

*   **SealedSecret:** A Custom Resource Definition (CRD) provided by the Sealed Secrets project.  You use this resource to define your encrypted secrets. It contains the encrypted Secret data, the namespace, and the name.

## Practical Implementation

Here's a step-by-step guide on how to implement Sealed Secrets:

**1. Install Kubeseal CLI Tool:**

Kubeseal is a command-line tool that's used to encrypt Kubernetes Secrets using the public key from the Sealed Secrets controller.

```bash
# Install on macOS (using Homebrew)
brew install kubeseal
```

```bash
# Download Linux binary:
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')
curl -sLo kubeseal https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.23.1/kubeseal-${OS}-${ARCH}
chmod +x kubeseal
sudo mv kubeseal /usr/local/bin
```

**2. Install the Sealed Secrets Controller on your Kubernetes Cluster:**

The easiest way to install the Sealed Secrets controller is using Helm:

```bash
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm repo update
helm install sealed-secrets sealed-secrets/sealed-secrets --namespace kube-system --create-namespace
```

Verify that the controller is running:

```bash
kubectl get pods -n kube-system | grep sealed-secrets
```

**3. Create a Kubernetes Secret:**

Let's create a simple Kubernetes Secret containing a database password.  For demonstration purposes, we'll define this secret in a YAML file called `my-secret.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-db-credentials
type: Opaque
data:
  username: $(echo -n 'myuser' | base64)
  password: $(echo -n 'mypassword' | base64)
```

Apply this secret to your cluster:

```bash
kubectl apply -f my-secret.yaml
```

**4. Encrypt the Secret using `kubeseal`:**

Now, we'll use `kubeseal` to encrypt the `my-db-credentials` secret. Make sure you are in the same directory as your `my-secret.yaml` file.

```bash
kubeseal --format yaml < my-secret.yaml > sealed-my-db-credentials.yaml
```

This command will:

*   Read the `my-secret.yaml` file.
*   Connect to your Kubernetes cluster to retrieve the public key from the Sealed Secrets controller.
*   Encrypt the Secret data using the public key.
*   Output the encrypted Secret in YAML format to a file named `sealed-my-db-credentials.yaml`.

Inspect the `sealed-my-db-credentials.yaml` file. It should look similar to this:

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  creationTimestamp: null
  name: my-db-credentials
  namespace: default
spec:
  encryptedData:
    password: AgB3... (long encrypted string)
    username: AgB4... (long encrypted string)
  template:
    data: null
    metadata:
      creationTimestamp: null
      name: my-db-credentials
      namespace: default
    type: Opaque
```

Notice that the `data` section within `spec.encryptedData` contains the encrypted values for `username` and `password`.  The `template` section mirrors the original Secret definition.

**5. Deploy the SealedSecret to your Kubernetes Cluster:**

Now, apply the `sealed-my-db-credentials.yaml` file to your Kubernetes cluster:

```bash
kubectl apply -f sealed-my-db-credentials.yaml
```

**6. Verify the Secret is Created:**

The Sealed Secrets controller will detect the newly created `SealedSecret` resource, decrypt it using its private key, and create a corresponding standard Kubernetes Secret object.

```bash
kubectl get secrets my-db-credentials
```

You should see a standard Kubernetes Secret named `my-db-credentials` in your namespace. The data inside of the secret will be the decrypted versions of the username and password that you defined in `my-secret.yaml`.

**7. Clean up:**

Since you used base64 encoded secrets in a normal Secret object originally, you'll want to delete it now that you have a sealed secret.

```bash
kubectl delete -f my-secret.yaml
```

## Common Mistakes

*   **Committing Unencrypted Secrets to Git:** This is the most common and critical mistake. Never commit raw Kubernetes Secrets to a public or private Git repository.

*   **Incorrectly Configuring `kubeseal`:**  Ensure that `kubeseal` is configured to connect to the correct Kubernetes cluster and namespace where the Sealed Secrets controller is running.  Verify your `kubeconfig` file is properly configured.

*   **Deleting the Sealed Secrets Controller:** Deleting the controller without a proper backup of the private key will make it impossible to decrypt existing SealedSecret resources.  Back up your controller if you ever decide to get rid of it.

*   **Using the Wrong Public Key:** Ensure you are using the public key associated with the Sealed Secrets controller running in your cluster.  `kubeseal` typically handles this automatically by connecting to your cluster, but manual extraction of the public key is possible, requiring extra care.

*   **Forgetting the `template` Section:** The `template` section in the `SealedSecret` defines the characteristics of the resulting Secret, like name, namespace, and type. If you don't include a proper template, the created Secret might not function as expected.

## Interview Perspective

When discussing Sealed Secrets in interviews, be prepared to discuss the following:

*   **The problem it solves:** Securely managing secrets in Kubernetes, especially in GitOps workflows.

*   **How it works:**  Public-key encryption, SealedSecrets controller, SealedSecret CRD.

*   **The advantages of using Sealed Secrets:**  Improved security, GitOps compatibility, simplified secret management.

*   **Alternatives to Sealed Secrets:**  Vault, SOPS, external secret stores.  Discuss the trade-offs between these solutions (e.g., complexity, operational overhead, feature set).

*   **Security considerations:** Key rotation, access control to the Sealed Secrets controller, proper RBAC configuration.

Key talking points:

*   Emphasize the importance of encryption at rest and the benefits of using an asymmetric encryption scheme.
*   Explain how Sealed Secrets facilitates GitOps by allowing you to store encrypted secrets in Git repositories.
*   Discuss the operational aspects of managing Sealed Secrets, such as controller installation, secret encryption, and deployment.
*   Be prepared to compare Sealed Secrets to other secret management solutions and justify your choice.

## Real-World Use Cases

*   **Storing Database Credentials:**  Encrypting database usernames, passwords, and connection strings to protect sensitive database access information.

*   **Managing API Keys:**  Safeguarding API keys used to access external services and APIs.

*   **Handling TLS Certificates:**  Storing encrypted TLS certificates used for securing communication between services.

*   **Automating Secret Rotation:**  Integrating Sealed Secrets with automation tools to automate the rotation of encrypted secrets.

*   **Implementing Secure Configuration Management:** Using Sealed Secrets to manage sensitive configuration data in a GitOps environment.

For example, consider a microservices architecture where each service requires access to a database.  Using Sealed Secrets, you can encrypt the database credentials for each service and store them in a Git repository.  The deployment pipeline can automatically deploy the encrypted secrets to the appropriate Kubernetes namespaces, and the Sealed Secrets controller will decrypt them into standard Kubernetes Secret objects, which the services can then consume. This ensures that the database credentials are never exposed in plain text, even during deployment.

## Conclusion

Sealed Secrets provide a practical and effective solution for managing secrets in Kubernetes, particularly when integrating with GitOps workflows. By leveraging public-key encryption, Sealed Secrets allow you to safely store your secrets in Git repositories, ensuring the confidentiality and integrity of your sensitive data.  By understanding the core concepts, following the implementation steps outlined in this blog post, and avoiding common mistakes, you can effectively use Sealed Secrets to enhance the security of your Kubernetes deployments. Remember to consider key rotation strategies and access control policies to further strengthen your security posture.
```