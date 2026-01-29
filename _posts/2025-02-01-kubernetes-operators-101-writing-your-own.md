yaml
---
layout: post
title: "Kubernetes Operators 101: Writing Your Own"
date: 2024-02-29
categories: [Tech, Engineering]
tags: [tech, software, engineering, kubernetes, operators, golang, controllers]
author: ritesh
---

## Introduction

Kubernetes has revolutionized the way we deploy and manage applications, providing powerful tools for orchestration, scaling, and resilience. However, managing complex applications often involves more than just deploying simple Pods. It requires handling custom resources, complex configurations, and automated operational tasks. This is where Kubernetes Operators come in. Operators extend the Kubernetes API to manage complex applications more easily and efficiently. Think of them as Kubernetes-native "application controllers," automating tasks typically performed by a human operator.

This blog post serves as a Kubernetes Operators 101 guide, walking you through the fundamental concepts and illustrating how to build your own Operator from scratch. We'll focus on the core components and provide practical code examples to help you get started. By the end of this tutorial, you'll understand the power and flexibility that Operators bring to Kubernetes application management.

## Core Concepts

Before diving into the implementation, it's crucial to understand the core concepts behind Kubernetes Operators.

*   **Custom Resource Definitions (CRDs):** CRDs are the cornerstone of Operators. They allow you to extend the Kubernetes API by defining your own custom resource types. For example, you could define a CRD for a "Database" resource, specifying attributes like database version, storage size, and replication settings.

*   **Custom Resources (CRs):** Once a CRD is defined, you can create instances of that resource, called Custom Resources. These CRs represent the desired state of your application. For our "Database" example, you might create a CR instance specifying the desired configuration for your specific database instance.

*   **Controllers:** Controllers are reconciliation loops that watch for changes to CRs and take actions to reconcile the actual state with the desired state defined in the CR. The controller constantly monitors the cluster and ensures that the application's state matches the CR definition. For our "Database" example, the controller would ensure that a database exists with the specified version, storage size, and replication settings, and that it is kept running.

*   **Operator:** An Operator is essentially a controller packaged with the CRDs and any necessary deployment manifests to run within a Kubernetes cluster. It's the complete unit of deployment for managing a particular application or component.

In summary, an Operator defines a new resource type (CRD), allows users to declare instances of that resource (CRs), and provides a controller to reconcile the actual state of the cluster to match the desired state declared in the CRs.

## Implementation: Building a Simple "MyApplication" Operator

Let's walk through building a basic Operator that manages a simple application called "MyApplication". This application will be represented by a CRD that defines the application's name and replicas.  We'll use the `controller-runtime` library which provides a high-level API for building controllers.

**1. Setting up the Project:**

We'll assume you have Go installed and configured. First, create a new Go module:

bash
mkdir my-application-operator
cd my-application-operator
go mod init github.com/your-username/my-application-operator


**2. Define the CRD:**

Create a file `api/v1alpha1/myapplication_types.go` with the following content:

go
package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// MyApplicationSpec defines the desired state of MyApplication
type MyApplicationSpec struct {
	// Name of the application
	Name string `json:"name"`
	// Number of replicas
	Replicas int32 `json:"replicas"`
}

// MyApplicationStatus defines the observed state of MyApplication
type MyApplicationStatus struct {
	// ReadyReplicas is the number of pods targeted by this application
	ReadyReplicas int32 `json:"readyReplicas"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// MyApplication is the Schema for the myapplications API
type MyApplication struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   MyApplicationSpec   `json:"spec,omitempty"`
	Status MyApplicationStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// MyApplicationList contains a list of MyApplication
type MyApplicationList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []MyApplication `json:"items"`
}

func init() {
	SchemeBuilder.Register(&MyApplication{}, &MyApplicationList{})
}



This code defines the `MyApplication` CRD, which has a `spec` containing the application's name and the desired number of replicas, and a `status` indicating the number of ready replicas.  The `//+kubebuilder:object:root=true` and `//+kubebuilder:subresource:status` markers are used by `controller-gen` to generate the CRD definition and enable status subresource functionality.

**3. Install `controller-gen` and Generate CRD manifests:**

bash
go install sigs.k8s.io/controller-tools/cmd/controller-gen@latest

# Add this line to the root directory's 'go.mod' file:
# +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
# +kubebuilder:rbac:groups=apps,resources=deployments/status,verbs=get

# run this in the root dir
controller-gen crd:generate paths=./api/v1alpha1/... output:crd:artifacts:config/crd/bases


This generates the CRD YAML manifest in `config/crd/bases`.  This manifest needs to be applied to your Kubernetes cluster before you can create `MyApplication` CRs.

**4. Implement the Controller:**

Create a file `controllers/myapplication_controller.go` with the following content:

{% raw %}
go
package controllers

import (
	"context"
	"fmt"

	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	myappv1alpha1 "github.com/your-username/my-application-operator/api/v1alpha1"
)

// MyApplicationReconciler reconciles a MyApplication object
type MyApplicationReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=myapp.example.com,resources=myapplications,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=myapp.example.com,resources=myapplications/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=myapp.example.com,resources=myapplications/finalizers,verbs=update
//+kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=core,resources=pods,verbs=get;list;watch

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// Modify the Reconcile function to compare the state specified by
// the MyApplication object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.14.1/pkg/reconcile
func (r *MyApplicationReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := log.FromContext(ctx)

	// 1. Fetch the MyApplication instance
	myApp := &myappv1alpha1.MyApplication{}
	err := r.Get(ctx, req.NamespacedName, myApp)
	if err != nil {
		// Error reading the object - requeue the request.
		log.Error(err, "unable to fetch MyApplication")
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	// 2. Check if the Deployment already exists, if not create a new one
	deployment := &appsv1.Deployment{}
	err = r.Get(ctx, client.ObjectKey{Namespace: myApp.Namespace, Name: myApp.Name}, deployment)
	if err != nil {
		if client.IgnoreNotFound(err) == nil {
			// Deployment doesn't exist, create it
			dep := r.deploymentForMyApplication(myApp)
			log.Info("Creating a new Deployment", "Deployment.Namespace", dep.Namespace, "Deployment.Name", dep.Name)
			err = r.Create(ctx, dep)
			if err != nil {
				log.Error(err, "Failed to create new Deployment", "Deployment.Namespace", dep.Namespace, "Deployment.Name", dep.Name)
				return ctrl.Result{}, err
			}
			// Deployment created successfully - return and requeue
			return ctrl.Result{Requeue: true}, nil
		} else {
			log.Error(err, "Failed to get Deployment")
			return ctrl.Result{}, err
		}
	}

	// 3. Ensure the deployment size is the same as the spec
	size := myApp.Spec.Replicas
	if *deployment.Spec.Replicas != size {
		deployment.Spec.Replicas = &size
		err = r.Update(ctx, deployment)
		if err != nil {
			log.Error(err, "Failed to update Deployment", "Deployment.Namespace", deployment.Namespace, "Deployment.Name", deployment.Name)
			return ctrl.Result{}, err
		}
		// Spec updated - return and requeue
		return ctrl.Result{Requeue: true}, nil
	}

	// Update the MyApplication status with the number of ready replicas
	podList := &corev1.PodList{}
	listOpts := []client.ListOption{
		client.InNamespace(myApp.Namespace),
		client.MatchingLabels(map[string]string{"app": myApp.Name}),
	}
	if err = r.List(ctx, podList, listOpts...); err != nil {
		log.Error(err, "Failed to list pods", "MyApplication.Namespace", myApp.Namespace, "MyApplication.Name", myApp.Name)
		return ctrl.Result{}, err
	}

	readyReplicas := int32(0)
	for _, pod := range podList.Items {
		if pod.Status.Phase == corev1.PodRunning {
			readyReplicas++
		}
	}
    myApp.Status.ReadyReplicas = readyReplicas
	err = r.Status().Update(ctx, myApp)

	if err != nil {
		log.Error(err, "Failed to update MyApplication status")
		return ctrl.Result{}, err
	}

	return ctrl.Result{}, nil
}

// deploymentForMyApplication returns a Deployment object for the MyApplication
func (r *MyApplicationReconciler) deploymentForMyApplication(m *myappv1alpha1.MyApplication) *appsv1.Deployment {
	ls := map[string]string{"app": m.Name}
	replicas := m.Spec.Replicas

	dep := &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name:      m.Name,
			Namespace: m.Namespace,
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
						Image:   "nginx:latest", // Or any other simple image
						Name:    "nginx",
						Ports: []corev1.ContainerPort{{
							ContainerPort: 80,
							Name:        "http",
						}},
					}},
				},
			},
		},
	}
	// Set MyApplication instance as the owner and controller
	ctrl.SetControllerReference(m, dep, r.Scheme)
	return dep
}

// SetupWithManager sets up the controller with the Manager.
func (r *MyApplicationReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&myappv1alpha1.MyApplication{}).
		Owns(&appsv1.Deployment{}).
		Complete(r)
}

{% endraw %}
This controller watches for changes to `MyApplication` resources.  When a new `MyApplication` resource is created, the controller creates a corresponding `Deployment`.  If the `MyApplication` resource is updated (e.g., the number of replicas changes), the controller updates the `Deployment` accordingly. It also updates the status of the custom resource reflecting the number of running pods.  It uses an Nginx image for simplicity.

**5. Modify `main.go`:**

In `main.go`, register the CRD scheme and the controller with the manager.  Modify the `main.go` file (usually located in the root directory) to include the following:

go
import (
	"flag"
	"os"

	// Import all Kubernetes client auth plugins (e.g. Azure, GCP, OIDC, etc.)
	// to ensure that exec-entrypoint and run after-entrypoint hook executables can use them.
	_ "k8s.io/client-go/plugin/pkg/client/auth"

	"k8s.io/apimachinery/pkg/runtime"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/healthz"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"

	myappv1alpha1 "github.com/your-username/my-application-operator/api/v1alpha1"
	"github.com/your-username/my-application-operator/controllers"
	//+kubebuilder:scaffold:imports
)

var (
	scheme   = runtime.NewScheme()
	setupLog = ctrl.Log.WithName("setup")
)

func init() {
	utilruntime.Must(clientgoscheme.AddToScheme(scheme))

	utilruntime.Must(myappv1alpha1.AddToScheme(scheme))
	//+kubebuilder:scaffold:scheme
}

func main() {
	var metricsAddr string
	var enableLeaderElection bool
	var probeAddr string
	flag.StringVar(&metricsAddr, "metrics-bind-address", ":8080", "The address the metric endpoint binds to.")
	flag.StringVar(&probeAddr, "health-probe-bind-address", ":8081", "The address the probe endpoint binds to.")
	flag.BoolVar(&enableLeaderElection, "leader-elect", false,
		"Enable leader election for controller manager. "+
			"Enabling this will ensure there is only one active controller manager.")
	opts := zap.Options{
		Development: true,
	}
	opts.BindFlags(flag.CommandLine)
	flag.Parse()

	ctrl.SetLogger(zap.New(zap.UseFlagOptions(&opts)))

	mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
		Scheme:                 scheme,
		MetricsBindAddress:     metricsAddr,
		Port:                   9443,
		HealthProbeBindAddress: probeAddr,
		LeaderElection:         enableLeaderElection,
		LeaderElectionID:       "f459d779.example.com",
		// LeaderElectionReleaseOnCancel defines if the leader should step down voluntarily
		// when the Manager ends. This requires the binrary to immediately end when the
		// Manager is stopped, otherwise, this setting is unsafe. Setting this significantly
		// speeds up voluntary leader transition as the new leader don't have to wait
		// LeaseDuration.
		// LeaderElectionReleaseOnCancel: true,
	})
	if err != nil {
		setupLog.Error(err, "unable to start manager")
		os.Exit(1)
	}

	if err = (&controllers.MyApplicationReconciler{
		Client: mgr.GetClient(),
		Scheme: mgr.GetScheme(),
	}).SetupWithManager(mgr); err != nil {
		setupLog.Error(err, "unable to create controller", "controller", "MyApplication")
		os.Exit(1)
	}
	//+kubebuilder:scaffold:builder

	if err := mgr.AddHealthzCheck("healthz", healthz.Ping); err != nil {
		setupLog.Error(err, "unable to set up health check")
		os.Exit(1)
	}
	if err := mgr.AddReadyzCheck("readyz", healthz.Ping); err != nil {
		setupLog.Error(err, "unable to set up ready check")
		os.Exit(1)
	}

	setupLog.Info("starting manager")
	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		setupLog.Error(err, "problem running manager")
		os.Exit(1)
	}
}


**6. Build and Deploy the Operator:**

Build the operator:

bash
go build -o bin/manager main.go


Then, deploy it to your Kubernetes cluster. You'll need to create a `config/manager/kustomization.yaml` file based on the controller-runtime documentation to define how to deploy the manager, and run `kubectl apply -k config/manager`. You also need to apply the CRD definition using `kubectl apply -f config/crd/bases/myapp.example.com_myapplications.yaml`. Finally, you'll need to create RBAC rules for the controller to function properly.  These are normally generated via the `controller-gen` tool and applied via `kubectl apply`.

**7. Create a `MyApplication` CR:**

Create a YAML file (e.g., `config/samples/myapplication.yaml`) to define a `MyApplication` resource:

yaml
apiVersion: myapp.example.com/v1alpha1
kind: MyApplication
metadata:
  name: my-app-instance
spec:
  name: my-app
  replicas: 3


Apply this to your cluster:

bash
kubectl apply -f config/samples/myapplication.yaml


You should see a Deployment named `my-app-instance` created with 3 replicas. The operator will automatically manage the deployment based on the custom resource you defined.

## Conclusion

This example provides a basic introduction to building Kubernetes Operators. While this is a simplified illustration, it demonstrates the fundamental concepts of CRDs, controllers, and reconciliation loops.  By leveraging these principles, you can automate the management of complex applications and streamline your Kubernetes operations. Further exploration into advanced features like webhooks, finalizers, and more complex reconciliation logic will allow you to build sophisticated operators tailored to your specific needs. Remember to consult the official Kubernetes and `controller-runtime` documentation for detailed information and best practices.
