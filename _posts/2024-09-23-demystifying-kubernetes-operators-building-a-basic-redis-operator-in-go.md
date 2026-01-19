---
title: "Demystifying Kubernetes Operators: Building a Basic Redis Operator in Go"
date: 2024-09-23 13:18:33 +0000
categories: [DevOps, Kubernetes]
tags: [kubernetes, operators, go, redis, controller, custom-resource-definition]
---

## Introduction

Kubernetes Operators are a powerful way to automate the management of complex applications within a Kubernetes cluster. Instead of manually managing resources and configurations, operators extend Kubernetes' API to encapsulate the operational knowledge required to manage a specific application, such as databases, message queues, or, in our case, a Redis cluster. This blog post will guide you through the process of building a basic Kubernetes Operator in Go for managing Redis instances. We'll focus on the core concepts and provide a practical, step-by-step implementation.

## Core Concepts

Before diving into the code, let's clarify some key concepts:

*   **Kubernetes Controller:**  At its heart, an Operator is a specialized controller. Controllers are reconciliation loops that continuously observe the desired state of the cluster and take actions to achieve that state. They typically listen for changes to specific Kubernetes resources.

*   **Custom Resource Definition (CRD):**  A CRD allows you to extend the Kubernetes API by defining new, custom resource types.  In our case, we'll create a CRD for representing a Redis instance. This allows users to define a Redis cluster in the same declarative way they manage other Kubernetes resources.

*   **Custom Resource (CR):** Once a CRD is defined, you can create instances of that resource, known as Custom Resources. For example, you might create a CR named "my-redis-cluster" based on our Redis CRD, specifying the desired number of replicas and memory limits.

*   **Operator SDK:** The Operator SDK simplifies the process of building Kubernetes Operators. It provides scaffolding, code generation, and best practices for creating robust and maintainable operators. We will leverage `kubebuilder`, which is now part of the Operator SDK.

*   **Reconciliation Loop:** This is the heart of the controller. The reconciliation loop observes the state of the Custom Resource (CR) and takes actions to bring the actual state into alignment with the desired state specified in the CR. For example, if the desired number of Redis replicas is 3, and only 2 replicas are running, the reconciliation loop will create a new replica.

## Practical Implementation

We'll use `kubebuilder` to scaffold our Redis Operator. Make sure you have Go and `kubebuilder` installed and properly configured.

**1. Project Setup:**

First, create a new project directory and initialize it with `kubebuilder`:

```bash
mkdir redis-operator
cd redis-operator
kubebuilder init --domain example.com --repo github.com/your-username/redis-operator
```

Replace `example.com` with your domain and `github.com/your-username/redis-operator` with your repository URL.

**2. Create the Redis CRD:**

Next, create the Redis CRD:

```bash
kubebuilder create api --group cache --version v1alpha1 --kind Redis
```

This command will generate the necessary Go code for the `Redis` resource in `api/v1alpha1/redis_types.go` and the controller logic in `controllers/redis_controller.go`.

**3. Define the Redis Resource Specification:**

Edit `api/v1alpha1/redis_types.go` to define the fields for our Redis resource:

```go
package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// RedisSpec defines the desired state of Redis
type RedisSpec struct {
	// Size is the desired size of the Redis deployment
	Size int32 `json:"size"`

	// Image is the Redis image to use
	Image string `json:"image,omitempty"`
}

// RedisStatus defines the observed state of Redis
type RedisStatus struct {
	// Nodes are the names of the redis pods
	Nodes []string `json:"nodes"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// Redis is the Schema for the redis API
type Redis struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   RedisSpec   `json:"spec,omitempty"`
	Status RedisStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// RedisList contains a list of Redis
type RedisList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Redis `json:"items"`
}

func init() {
	SchemeBuilder.Register(&Redis{}, &RedisList{})
}
```

We added `Size` and `Image` to the `RedisSpec`, representing the number of Redis replicas and the Docker image to use, respectively. `RedisStatus` tracks the names of running pods.

**4. Implement the Reconciliation Logic:**

Now, let's implement the reconciliation logic in `controllers/redis_controller.go`. This is where the magic happens. We'll create Deployments and Services for our Redis instances.

```go
package controllers

import (
	"context"
	"fmt"

	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	cachev1alpha1 "github.com/your-username/redis-operator/api/v1alpha1"
)

// RedisReconciler reconciles a Redis object
type RedisReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=cache.example.com,resources=redis,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=cache.example.com,resources=redis/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=cache.example.com,resources=redis/finalizers,verbs=update
//+kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=core,resources=pods,verbs=get;list;watch

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.14.1/pkg/reconcile
func (r *RedisReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := log.FromContext(ctx)

	// 1. Fetch the Redis resource
	redis := &cachev1alpha1.Redis{}
	err := r.Get(ctx, req.NamespacedName, redis)
	if err != nil {
		if errors.IsNotFound(err) {
			log.Info("Redis resource not found. Ignoring since object must be deleted")
			return ctrl.Result{}, nil
		}
		log.Error(err, "Failed to get Redis resource")
		return ctrl.Result{}, err
	}

	// 2. Define a new Deployment
	deployment := r.deploymentForRedis(redis)

	// 3. Check if the Deployment already exists, if not create a new one
	found := &appsv1.Deployment{}
	err = r.Get(ctx, types.NamespacedName{Name: deployment.Name, Namespace: deployment.Namespace}, found)
	if err != nil {
		if errors.IsNotFound(err) {
			log.Info("Creating a new Deployment", "Deployment.Namespace", deployment.Namespace, "Deployment.Name", deployment.Name)
			err = r.Create(ctx, deployment)
			if err != nil {
				log.Error(err, "Failed to create new Deployment", "Deployment.Namespace", deployment.Namespace, "Deployment.Name", deployment.Name)
				return ctrl.Result{}, err
			}
			// Deployment created successfully - return and requeue
			return ctrl.Result{Requeue: true}, nil
		}
		log.Error(err, "Failed to get Deployment")
		return ctrl.Result{}, err
	}

	// 4. Ensure the deployment size is the same as the spec
	size := redis.Spec.Size
	if *found.Spec.Replicas != size {
		found.Spec.Replicas = &size
		err = r.Update(ctx, found)
		if err != nil {
			log.Error(err, "Failed to update Deployment", "Deployment.Namespace", found.Namespace, "Deployment.Name", found.Name)
			return ctrl.Result{}, err
		}
		// Spec updated - return and requeue
		return ctrl.Result{Requeue: true}, nil
	}

	// 5. Update the Redis status with the pod names
	podList := &corev1.PodList{}
	listOpts := []client.ListOption{
		client.InNamespace(req.Namespace),
		client.MatchingLabels(labelsForRedis(redis.Name)),
	}
	if err = r.List(ctx, podList, listOpts...); err != nil {
		log.Error(err, "Failed to list pods", "Redis.Namespace", redis.Namespace, "Redis.Name", redis.Name)
		return ctrl.Result{}, err
	}
	podNames := getPodNames(podList.Items)
	if !reflect.DeepEqual(podNames, redis.Status.Nodes) {
		redis.Status.Nodes = podNames
		err := r.Status().Update(ctx, redis)
		if err != nil {
			log.Error(err, "Failed to update Redis status")
			return ctrl.Result{}, err
		}
		return ctrl.Result{}, nil
	}

	return ctrl.Result{}, nil
}

// deploymentForRedis returns a redis Deployment object
func (r *RedisReconciler) deploymentForRedis(redis *cachev1alpha1.Redis) *appsv1.Deployment {
	ls := labelsForRedis(redis.Name)
	replicas := redis.Spec.Size

	dep := &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name:      redis.Name,
			Namespace: redis.Namespace,
			Labels: ls,
		},
		Spec: appsv1.DeploymentSpec{
			Replicas: &replicas,
			Selector: &metav1.LabelSelector{
				MatchLabels: ls,
			},
			Template: corev1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: ls,
				},
				Spec: corev1.PodSpec{
					Containers: []corev1.Container{{
						Image:   redis.Spec.Image,
						Name:    "redis",
						Ports: []corev1.ContainerPort{{
							ContainerPort: 6379,
							Name:          "redis",
						}},
					}},
				},
			},
		},
	}
	// Set Redis instance as the owner and controller
	ctrl.SetControllerReference(redis, dep, r.Scheme)
	return dep
}

// labelsForRedis returns the labels for selecting the resources
// belonging to the given redis CR name.
func labelsForRedis(name string) map[string]string {
	return map[string]string{"app": "redis", "redis_cr": name}
}

// getPodNames returns the pod names of the array of pods passed in
func getPodNames(pods []corev1.Pod) []string {
	var podNames []string
	for _, pod := range pods {
		podNames = append(podNames, pod.Name)
	}
	return podNames
}

// SetupWithManager sets up the controller with the Manager.
func (r *RedisReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&cachev1alpha1.Redis{}).
		Owns(&appsv1.Deployment{}).
		Complete(r)
}
```

**5. Build and Deploy the Operator:**

Run the following commands to build and deploy the operator to your Kubernetes cluster:

```bash
make docker-build docker-push IMG="your-docker-repo/redis-operator:latest"
make deploy IMG="your-docker-repo/redis-operator:latest"
```

Remember to replace `your-docker-repo/redis-operator:latest` with your actual Docker repository.

**6. Create a Redis Custom Resource:**

Now create a `redis.yaml` file:

```yaml
apiVersion: cache.example.com/v1alpha1
kind: Redis
metadata:
  name: my-redis
spec:
  size: 3
  image: redis:latest
```

Apply it to your cluster:

```bash
kubectl apply -f redis.yaml
```

You should now see three Redis pods running in your cluster.

## Common Mistakes

*   **Missing RBAC Permissions:**  Ensure your operator has the necessary RBAC permissions to create, read, update, and delete resources. The `//+kubebuilder:rbac` markers in the controller code are crucial for this.
*   **Incorrect Controller Reference:**  Properly setting the controller reference using `ctrl.SetControllerReference` ensures that the Kubernetes garbage collector cleans up resources created by the operator when the CR is deleted.
*   **Ignoring Errors:**  Always check for errors when interacting with the Kubernetes API and handle them gracefully.  Logging errors is vital for debugging.
*   **Not Requeuing:**  If the reconciliation loop needs to perform asynchronous operations, make sure to requeue the request to ensure the controller eventually reaches the desired state.
*   **Immutable Fields:**  Be careful about handling immutable fields. For example, if you need to change an immutable field in a Deployment, you'll need to recreate the Deployment.

## Interview Perspective

When discussing Kubernetes Operators in interviews, be prepared to answer the following:

*   **What is a Kubernetes Operator and why are they useful?**  Emphasize the automation and operational knowledge encapsulation aspects.
*   **What are the core components of an Operator?**  CRDs, CRs, and Controllers.
*   **Explain the reconciliation loop.**  How the controller observes the desired state and takes actions to achieve it.
*   **Describe the challenges of building Operators.**  RBAC, error handling, dealing with immutable fields, state management.
*   **Have you used Operator SDKs? If so, which ones and what were your experiences?** `kubebuilder` is a common choice.
*   **Describe a scenario where you would use an Operator.**  Managing a complex database cluster, automating deployments of microservices, etc.

Key talking points include: Automation, Custom Resources, Reconciliation, Operational Expertise, Scalability, and Maintainability.

## Real-World Use Cases

Operators are widely used for:

*   **Databases:** Managing databases like PostgreSQL, MySQL, and Cassandra.
*   **Message Queues:** Managing message queues like Kafka and RabbitMQ.
*   **CI/CD Systems:** Automating deployments and managing CI/CD pipelines.
*   **Monitoring Systems:** Deploying and configuring monitoring tools like Prometheus and Grafana.
*   **AI/ML Workloads:** Managing complex AI/ML training and inference pipelines.

## Conclusion

This blog post has provided a practical introduction to building Kubernetes Operators using Go and `kubebuilder`. While this example is a basic Redis Operator, it demonstrates the fundamental concepts and steps involved in creating more complex operators for managing a wide range of applications.  By leveraging Operators, you can significantly simplify the management of your applications within a Kubernetes environment, improving automation, scalability, and overall operational efficiency. Remember to focus on robust error handling, proper RBAC configuration, and a well-defined reconciliation loop for building reliable and maintainable operators.
