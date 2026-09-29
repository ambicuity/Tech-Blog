---
layout: post
title: "Setting up a K8s Cluster on Bare Metal"
date: 2024-02-29
categories: [Kubernetes, Platform Engineering]
tags: [kubernetes, bare-metal, deployment-strategies]
author: ritesh
---

## Introduction

Kubernetes (K8s) has become the de facto standard for container orchestration. While cloud-based Kubernetes solutions like Google Kubernetes Engine (GKE), Amazon Elastic Kubernetes Service (EKS), and Azure Kubernetes Service (AKS) offer managed services, setting up a Kubernetes cluster on bare metal infrastructure provides greater control and potentially lower long-term costs, especially for organizations with existing hardware investments. This post will guide you through the process of setting up a functional Kubernetes cluster on bare metal, highlighting key concepts and practical implementation steps. We'll focus on a streamlined approach using tools like `kubeadm`, `kubectl`, and a suitable container runtime.

## Core Concepts

Before diving into the implementation, let's clarify some fundamental concepts:

*   **Kubernetes Architecture:** A Kubernetes cluster consists of a control plane and worker nodes. The **control plane** manages the cluster, making decisions about scheduling, monitoring, and maintaining the desired state. It comprises components like the API server, scheduler, controller manager, and etcd (a distributed key-value store). **Worker nodes** are the machines that run your containerized applications.  They host Pods, which are the smallest deployable units in Kubernetes.

*   **kubeadm:** A command-line tool designed to bootstrap Kubernetes clusters. It simplifies the process of initializing a control plane and joining worker nodes. `kubeadm` handles much of the complexity of setting up core Kubernetes components.

*   **kubectl:** The Kubernetes command-line tool that allows you to interact with the cluster. You use `kubectl` to deploy applications, inspect resources, and manage cluster operations.

*   **Container Runtime:** Kubernetes requires a container runtime to run containers. Popular choices include Containerd and CRI-O. We'll use Containerd in this guide.

*   **Networking:** A crucial aspect of Kubernetes is the networking layer, enabling communication between Pods, Services, and the outside world. A Container Network Interface (CNI) plugin manages this networking. Popular choices include Calico, Flannel, and Cilium. We'll use Calico for its robustness and advanced features.

*   **Bare Metal Considerations:** Setting up on bare metal means you are responsible for the underlying infrastructure, including operating system installation, network configuration, and storage provisioning. This adds complexity compared to managed Kubernetes services but offers greater flexibility.

## Implementation

This guide assumes you have at least three machines: one for the control plane (master node) and two for worker nodes. All machines should have a compatible Linux distribution (e.g., Ubuntu Server 20.04 or later, CentOS 7 or 8) and internet access. Ensure each machine has a unique hostname and a static IP address.

**Step 1: Prepare the Machines**

On all machines (control plane and worker nodes), perform the following steps:

1.  **Install Containerd:**

    bash
    # Install dependencies
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

    # Add the Docker GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Add the Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Update and install containerd
    sudo apt-get update
    sudo apt-get install -y containerd.io

    # Configure Containerd (create /etc/containerd/config.toml if it doesn't exist)
    sudo mkdir -p /etc/containerd
    sudo containerd config default | sudo tee /etc/containerd/config.toml

    # Restart Containerd
    sudo systemctl restart containerd
    sudo systemctl enable containerd
    

2.  **Install kubeadm, kubelet, and kubectl:**

    bash
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl

    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

    cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
    deb https://apt.kubernetes.io/ kubernetes-xenial main
    EOF

    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl
    

3.  **Disable Swap:** Kubernetes requires swap to be disabled for proper operation.

    bash
    sudo swapoff -a
    sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
    

**Step 2: Initialize the Control Plane**

On the designated control plane machine, execute the following:

bash
sudo kubeadm init --pod-network-cidr=192.168.0.0/16


*   `--pod-network-cidr`:  Specifies the IP address range for Pods.  Choose a CIDR block that doesn't overlap with your existing network.  `192.168.0.0/16` is a common example.

After the command completes successfully, `kubeadm init` will output a `kubeadm join` command.  **Copy this command and save it for later use on the worker nodes.** The output will resemble this:


kubeadm join <control-plane-ip>:<port> --token <token> --discovery-token-ca-cert-hash sha256:<hash>


Also, the output will display instructions to configure `kubectl`. Run these commands on the control plane node to be able to manage the cluster:

bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config


**Step 3: Install a Network Plugin (Calico)**

On the control plane machine, install a CNI plugin. We'll use Calico:

bash
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml


This command applies a Kubernetes manifest file that sets up Calico in your cluster. Verify that the Calico pods are running correctly:

bash
kubectl get pods -n kube-system


You should see pods related to Calico with a status of "Running".

**Step 4: Join Worker Nodes**

On each worker node, execute the `kubeadm join` command that you copied from the control plane node's output. For example:

bash
sudo kubeadm join <control-plane-ip>:<port> --token <token> --discovery-token-ca-cert-hash sha256:<hash>


**Step 5: Verify the Cluster**

Back on the control plane machine, verify that the worker nodes have joined the cluster:

bash
kubectl get nodes


You should see the control plane node and all worker nodes listed, with a status of "Ready".

## Example: Deploying a Simple Application

Now that the cluster is set up, let's deploy a simple application to verify its functionality. We'll deploy a basic Nginx deployment:

yaml
# nginx-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 2
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
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: NodePort


Deploy the application:

bash
kubectl apply -f nginx-deployment.yaml


Check the status of the deployment and service:

bash
kubectl get deployments
kubectl get services


To access the Nginx service, find the NodePort assigned to the service (e.g., `30080`) and access it through any worker node's IP address and that port (e.g., `http://<worker-node-ip>:30080`).

## Conclusion

Setting up a Kubernetes cluster on bare metal requires careful planning and execution. This guide provides a streamlined approach using `kubeadm` and Calico. While it covers the essential steps, remember that bare metal deployments introduce complexities related to infrastructure management. Thoroughly understanding Kubernetes concepts, network configuration, and storage provisioning is crucial for a successful and stable cluster. Consider exploring further topics like persistent storage, monitoring, and security hardening to optimize your bare metal Kubernetes environment. This setup provides you with a highly customizable and powerful platform for deploying and managing your containerized applications.
