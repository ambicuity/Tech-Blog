---
title: "Demystifying Kubernetes Operators: Building a Simple Etcd Operator in Go"
date: 2023-10-27 14:30:00 +0000
categories: [DevOps, Kubernetes]
tags: [kubernetes, operators, go, etcd, controller, custom-resource-definitions]
---

## Introduction

Kubernetes Operators are a powerful concept for automating the management of complex stateful applications within a Kubernetes cluster. Instead of manually configuring and maintaining applications like databases, message queues, or key-value stores, Operators encapsulate the operational knowledge into code, making deployments, scaling, backups, and other tasks significantly easier and more reliable. This blog post will demystify Kubernetes Operators by guiding you through building a simple Etcd Operator using Go. We'll cover the core concepts, practical implementation, common pitfalls, and real-world use cases to provide a comprehensive understanding of this valuable technology.

## Core Concepts

Before diving into the implementation, let's define some essential concepts:

*   **Custom Resource Definitions (CRDs):** CRDs allow you to extend the Kubernetes API by defining your own custom resources.  Imagine defining a resource called `EtcdCluster`, which allows you to define Etcd clusters directly in your Kubernetes manifests, just like you define Pods or Services. This is done via a YAML file that describes the schema of your new resource.

*   **Custom Resources (CRs):** These are instances of your CRDs. If you've defined an `EtcdCluster` CRD, creating a YAML file describing a specific Etcd cluster configuration with desired number of members, version, and storage details defines an EtcdCluster CR.

*   **Controllers:** Controllers are reconciliation loops that observe the state of your cluster (including CRs) and take actions to bring the actual state in line with the desired state defined in the CRs. Think of them as the "brains" of the Operator. The controller watches for changes to the EtcdCluster CR and then creates, updates, or deletes Etcd pods and services to match the configuration.

*   **Operator:**  An Operator is essentially a controller that specifically manages a particular application or service (like Etcd in our case) by leveraging CRDs and CRs. It automates the tasks that a human operator would normally perform.

*   **Reconciliation Loop:** The core logic within a controller. The controller continuously monitors the desired state (defined in the CR) and the current state. If a difference exists, it takes action to reconcile the current state to match the desired state.

## Practical Implementation

We'll create a simplified Etcd Operator. This operator will manage a single Etcd instance.

**1. Setting Up the Environment**

*   Ensure you have Go installed (version 1.16 or higher).
*   Install `kubectl` and `minikube` or a similar Kubernetes cluster.
*   Install `kustomize` - this is helpful to manage Kubernetes resources.
*   Initialize a Go project: `go mod init etcd-operator`

**2. Define the CRD (etcdcluster.yaml)**

Create a file named `etcdcluster.yaml` with the following content:

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: etcdclusters.stable.example.com
spec:
  group: stable.example.com
  versions:
    - name: v1alpha1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                size:
                  type: integer
                  description: The number of members in the Etcd cluster.
                  default: 1
  scope: Namespaced
  names:
    plural: etcdclusters
    singular: etcdcluster
    kind: EtcdCluster
    shortNames:
      - etcd
```

Apply the CRD to your cluster: `kubectl apply -f etcdcluster.yaml`

**3. Define the Custom Resource (example-etcdcluster.yaml)**

Create a file named `example-etcdcluster.yaml`:

```yaml
apiVersion: stable.example.com/v1alpha1
kind: EtcdCluster
metadata:
  name: example-etcd
spec:
  size: 1
```

This defines a single-node Etcd cluster named "example-etcd". Apply this resource: `kubectl apply -f example-etcdcluster.yaml`

**4. Building the Operator (main.go)**

```go
package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"time"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
	"k8s.io/klog/v2"

	"stable.example.com/etcd-operator/pkg/apis/etcd/v1alpha1"
	etcdclientset "stable.example.com/etcd-operator/pkg/client/clientset/versioned"
)

func main() {
	var kubeconfig *string
	if home := homedir.HomeDir(); home != "" {
		kubeconfig = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "(optional) absolute path to the kubeconfig file")
	} else {
		kubeconfig = flag.String("kubeconfig", "", "absolute path to the kubeconfig file")
	}
	flag.Parse()

	// 1. Create the client config. Use kubeconfig if given, otherwise assume in-cluster.
	config, err := buildConfig(*kubeconfig)
	if err != nil {
		klog.Fatal(err)
	}

	// 2. Create the clientset
	kubeClient, err := kubernetes.NewForConfig(config)
	if err != nil {
		klog.Fatal(err)
	}

	etcdClient, err := etcdclientset.NewForConfig(config)
	if err != nil {
		klog.Fatal(err)
	}

	// 3. Define your reconciliation loop
	for {
		// List all EtcdCluster resources
		etcdClusters, err := etcdClient.StableV1alpha1().EtcdClusters("default").List(context.TODO(), metav1.ListOptions{})
		if err != nil {
			klog.Errorf("Failed to list EtcdClusters: %v", err)
			time.Sleep(5 * time.Second)
			continue
		}

		for _, etcdCluster := range etcdClusters.Items {
			// Check if an Etcd pod already exists for this cluster
			podName := fmt.Sprintf("%s-etcd", etcdCluster.Name)
			_, err := kubeClient.CoreV1().Pods("default").Get(context.TODO(), podName, metav1.GetOptions{})

			if err != nil { // If the pod does not exist, create one
				// Define the Etcd pod
				pod := createEtcdPod(&etcdCluster)

				// Create the pod
				_, err = kubeClient.CoreV1().Pods("default").Create(context.TODO(), pod, metav1.CreateOptions{})
				if err != nil {
					klog.Errorf("Failed to create Etcd pod: %v", err)
				} else {
					klog.Infof("Etcd pod created: %s", podName)
				}
			} else {
				klog.Infof("Etcd pod already exists: %s", podName)
			}
		}

		time.Sleep(10 * time.Second)
	}
}

func buildConfig(kubeconfig string) (*rest.Config, error) {
	if kubeconfig != "" {
		cfg, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
		if err != nil {
			return nil, err
		}
		return cfg, nil
	}
	cfg, err := rest.InClusterConfig()
	if err != nil {
		return nil, err
	}
	return cfg, nil
}

func createEtcdPod(etcdCluster *v1alpha1.EtcdCluster) *v1.Pod {
	podName := fmt.Sprintf("%s-etcd", etcdCluster.Name)
	labels := map[string]string{
		"app":  "etcd",
		"name": podName,
	}

	pod := &v1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      podName,
			Namespace: "default",
			Labels:    labels,
			OwnerReferences: []metav1.OwnerReference{
				*metav1.NewControllerRef(etcdCluster, schema.GroupVersionKind{
					Group:   v1alpha1.SchemeGroupVersion.Group,
					Version: v1alpha1.SchemeGroupVersion.Version,
					Kind:    "EtcdCluster",
				}),
			},
		},
		Spec: v1.PodSpec{
			Containers: []v1.Container{
				{
					Name:            "etcd",
					Image:           "quay.io/coreos/etcd:v3.5.9",
					Ports:           []v1.ContainerPort{{ContainerPort: 2379}},
					ImagePullPolicy: v1.PullIfNotPresent,
				},
			},
		},
	}
	return pod
}
```

**5. Custom Resource Definition Go Bindings**

We need Go bindings for our CRD. We'll use `controller-gen` to generate them.

*   Install `controller-gen`: `go install sigs.k8s.io/controller-tools/cmd/controller-gen@latest`

Create the following directory structure:

```
etcd-operator/
├── pkg/
│   └── apis/
│       └── etcd/
│           └── v1alpha1/
```

Create `pkg/apis/etcd/v1alpha1/types.go`:

```go
package v1alpha1

import (
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// +genclient
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// EtcdCluster is a specification for a EtcdCluster resource
type EtcdCluster struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   EtcdClusterSpec   `json:"spec"`
    Status EtcdClusterStatus `json:"status"`
}

// EtcdClusterSpec is the spec for a EtcdCluster resource
type EtcdClusterSpec struct {
    Size int32 `json:"size"`
}

// EtcdClusterStatus is the status for a EtcdCluster resource
type EtcdClusterStatus struct {
    Nodes []string `json:"nodes"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// EtcdClusterList is a list of EtcdCluster resources
type EtcdClusterList struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata"`

    Items []EtcdCluster `json:"items"`
}
```

Create `pkg/apis/etcd/v1alpha1/doc.go`:

```go
// +k8s:deepcopy-gen=package
// +groupName=stable.example.com

package v1alpha1
```

Create `pkg/apis/etcd/register.go`:

```go
package etcd

import (
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"stable.example.com/etcd-operator/pkg/apis/etcd/v1alpha1"
)

const (
	GroupName = "stable.example.com"
)

var (
	SchemeGroupVersion = schema.GroupVersion{Group: GroupName, Version: "v1alpha1"}

	SchemeBuilder = runtime.NewSchemeBuilder(addKnownTypes)

	AddToScheme = SchemeBuilder.AddToScheme
)

func addKnownTypes(scheme *runtime.Scheme) error {
	scheme.AddKnownTypes(SchemeGroupVersion,
		&v1alpha1.EtcdCluster{},
		&v1alpha1.EtcdClusterList{},
	)

	metav1.AddToGroupVersion(scheme, SchemeGroupVersion)
	return nil
}
```

Now, generate the code:

```bash
controller-gen object:headerFile="hack/boilerplate.go.txt" paths="./..."
```

**6. Generate ClientSet and Informer**
```bash
mkdir -p pkg/client/clientset/versioned
mkdir -p pkg/client/informers/externalversions
mkdir -p pkg/client/listers

go install k8s.io/code-generator/cmd/client-gen@latest
go install k8s.io/code-generator/cmd/informer-gen@latest
go install k8s.io/code-generator/cmd/lister-gen@latest

client-gen \
  --go-header-file hack/boilerplate.go.txt \
  --clientset-name versioned \
  --input-base stable.example.com/etcd-operator/pkg/apis \
  --input stable.example.com/etcd-operator/pkg/apis/etcd/v1alpha1 \
  --output-package stable.example.com/etcd-operator/pkg/client

informer-gen \
  --go-header-file hack/boilerplate.go.txt \
  --clientset-package stable.example.com/etcd-operator/pkg/client/clientset/versioned \
  --versioned-clientset=true \
  --input-base stable.example.com/etcd-operator/pkg/apis \
  --input stable.example.com/etcd-operator/pkg/apis/etcd/v1alpha1 \
  --output-package stable.example.com/etcd-operator/pkg/client

lister-gen \
  --go-header-file hack/boilerplate.go.txt \
  --input-base stable.example.com/etcd-operator/pkg/apis \
  --input stable.example.com/etcd-operator/pkg/apis/etcd/v1alpha1 \
  --output-package stable.example.com/etcd-operator/pkg/client
```

**7. Run the Operator**

Run your operator: `go run main.go`

The operator will now create an Etcd pod based on the `example-etcdcluster.yaml` custom resource.

## Common Mistakes

*   **Incorrect CRD Definition:** A malformed CRD can cause the Kubernetes API server to reject your custom resources.  Carefully validate your YAML and schema.

*   **Missing Owner References:**  Setting the owner reference ensures that Kubernetes cleans up resources when the CR is deleted.  This is crucial for preventing orphaned resources.

*   **Improper Error Handling:**  Always handle errors gracefully in the reconciliation loop.  Logging errors is critical for debugging.

*   **Ignoring Deletion:**  Controllers must handle the deletion of CRs, including gracefully shutting down the managed application. Implementing finalizers will help handle deletion events.

*   **Not using Informers and Caches:** Using the Kubernetes API directly for every reconciliation loop can overload the API server. Use informers and caches to retrieve resource state efficiently.

## Interview Perspective

Interviewers often ask about:

*   **Understanding of CRDs and Operators:** Explain the purpose and benefits.
*   **Reconciliation Loop:** Describe the core logic and its importance.
*   **Error Handling and Logging:** Emphasize the importance of robust error handling.
*   **Scalability and Performance:**  Discuss how to optimize the operator for large-scale deployments.
*   **Ownership Management:** Explain how owner references work.

Key talking points:

*   Operators automate complex application management.
*   CRDs extend the Kubernetes API.
*   The reconciliation loop ensures desired state.
*   Operators enhance reliability and scalability.

## Real-World Use Cases

*   **Database Management (PostgreSQL, MySQL):** Automate database deployments, backups, and scaling.  Operators can manage complex configurations and ensure data consistency.
*   **Message Queue Management (Kafka, RabbitMQ):** Simplify the deployment and management of distributed message queues.
*   **AI/ML Model Serving:** Deploy and manage machine learning models with automated scaling and versioning.
*   **Monitoring Systems (Prometheus):** Manage the lifecycle of Prometheus deployments and configurations.

## Conclusion

Kubernetes Operators provide a powerful way to automate application management within Kubernetes. By understanding the core concepts and following best practices, you can build operators that simplify deployments, enhance reliability, and scale your applications with ease. This example provides a basic introduction, but more complex operators involve advanced topics like handling updates, rolling deployments, and scaling. Remember to leverage community resources and existing operators as inspiration for your own projects.
