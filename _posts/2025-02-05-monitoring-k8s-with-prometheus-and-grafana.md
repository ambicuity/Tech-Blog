---
layout: post
title: "Monitoring K8s with Prometheus and Grafana"
date: 2024-01-25
categories: [Reliability, Kubernetes]
tags: [kubernetes, prometheus, grafana, observability]
author: ritesh
---

## Introduction

Kubernetes has become the de facto standard for container orchestration, enabling developers to deploy and manage applications at scale. However, the dynamic and distributed nature of Kubernetes environments presents unique monitoring challenges. Without proper monitoring, identifying performance bottlenecks, debugging issues, and ensuring application health becomes significantly harder. This post delves into how to leverage Prometheus and Grafana for robust monitoring of your Kubernetes clusters, providing actionable insights to optimize performance and maintain stability. We'll explore the core concepts, installation, configuration, and practical examples to get you started.

## Core Concepts

Before diving into the implementation, let's establish a clear understanding of Prometheus and Grafana and how they work together:

*   **Prometheus:** An open-source systems monitoring and alerting toolkit. It scrapes metrics from configured targets at specified intervals, evaluates rule expressions, displays the results, and can trigger alerts if certain conditions are met. Prometheus is primarily a time-series database, optimized for storing numerical data indexed by time.
*   **Grafana:** An open-source data visualization and monitoring platform. It allows you to query, visualize, alert on, and explore your metrics no matter where they are stored. Grafana provides a user-friendly interface for building dashboards, allowing you to create insightful visualizations of your Prometheus data.
*   **Metrics:** Numerical data collected and tracked over time. In the context of Kubernetes, metrics can include CPU usage, memory consumption, network traffic, request latency, and more.
*   **Exporters:** Components that expose metrics in a format that Prometheus can scrape. For Kubernetes, several exporters are available, including kube-state-metrics, node-exporter, and cAdvisor.
*   **Service Discovery:** Prometheus can automatically discover targets to scrape metrics from, which is crucial in dynamic Kubernetes environments where pods and services are frequently created and destroyed. Kubernetes itself serves as a service discovery mechanism for Prometheus.

## Implementation

Now, let's walk through the steps to set up Prometheus and Grafana for monitoring a Kubernetes cluster. We'll focus on deploying them within the cluster itself. This guide assumes you already have a running Kubernetes cluster.

### Step 1: Deploying Prometheus

There are several ways to deploy Prometheus in Kubernetes, including using Helm, Operator, or manually applying Kubernetes manifests. We'll use Helm, which simplifies the deployment and management process.

First, add the Prometheus Helm repository:

bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update


Next, install Prometheus using Helm:

bash
helm install prometheus prometheus-community/prometheus


This command deploys Prometheus with its default configuration. For more customized installations, you can create a `values.yaml` file to override the default settings. For example, you might want to configure persistent storage:

yaml
# values.yaml
server:
  persistentVolume:
    enabled: true
    size: 10Gi


Then, install Prometheus with your custom configuration:

bash
helm install prometheus prometheus-community/prometheus -f values.yaml


To access the Prometheus UI, you can use port forwarding:

bash
kubectl port-forward svc/prometheus-server 9090:80


Then, open your browser and navigate to `http://localhost:9090`.

### Step 2: Deploying Grafana

Similarly, we can deploy Grafana using Helm.

First, add the Grafana Helm repository:

bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update


Next, install Grafana using Helm:

bash
helm install grafana grafana/grafana


To access the Grafana UI, use port forwarding:

bash
kubectl port-forward svc/grafana 3000:3000


Open your browser and navigate to `http://localhost:3000`. The default username is `admin` and the default password is `admin`. You'll be prompted to change the password upon first login.

### Step 3: Configuring Prometheus as a Data Source in Grafana

After deploying Prometheus and Grafana, we need to configure Grafana to use Prometheus as a data source.

1.  Log in to the Grafana UI.
2.  Navigate to "Connections" -> "Data sources" -> "Add data source".
3.  Select "Prometheus".
4.  Enter the Prometheus server URL.  Since both are running inside the cluster, use the Prometheus service name: `http://prometheus-server.default.svc.cluster.local`. Replace `default` with the namespace where Prometheus is deployed, if necessary.  If you've exposed Prometheus outside of the cluster, use the appropriate external address.
5.  Click "Save & test".  You should see a "Data source is working" message.

### Step 4: Installing Kubernetes Monitoring Dashboards

Grafana offers a rich ecosystem of pre-built dashboards for Kubernetes monitoring. These dashboards provide valuable insights into the health and performance of your cluster.  You can find many useful dashboards on the Grafana Labs website or inside the Grafana UI.

One popular dashboard is the "Kubernetes Cluster Monitoring (via Prometheus)" dashboard, ID `6417`.

To import a dashboard:

1.  In Grafana, navigate to "Dashboards" -> "New" -> "Import".
2.  Enter the dashboard ID (e.g., `6417`) or upload a dashboard JSON file.
3.  Select the Prometheus data source you configured in the previous step.
4.  Click "Import".

This dashboard provides a comprehensive overview of your Kubernetes cluster, including CPU usage, memory consumption, network traffic, and more.

### Step 5: Deploying Node Exporter and Kube-State-Metrics

To get detailed metrics about your nodes and Kubernetes resources, you'll need to deploy the node exporter and kube-state-metrics.

**Node Exporter:** This exporter exposes hardware and OS metrics from each node in your cluster. Deploy it as a DaemonSet to ensure it runs on every node.

bash
helm install prometheus-node-exporter prometheus-community/prometheus-node-exporter


**Kube-State-Metrics:** This exporter generates metrics based on the state of Kubernetes objects (pods, deployments, services, etc.).

bash
helm install kube-state-metrics prometheus-community/kube-state-metrics


Prometheus will automatically discover these exporters if they're deployed within the same Kubernetes cluster and configured to be scraped using service discovery.  The default Helm charts are typically configured to allow this auto-discovery via labels on the services.

## Configuration and Customization

The default configurations of Prometheus and Grafana are a good starting point, but you'll likely need to customize them to meet your specific monitoring needs.

*   **Prometheus Configuration:**  Modify the `prometheus.yml` configuration file (accessible through the Helm chart) to define scrape configurations, alerting rules, and recording rules.  Scrape configurations define which targets Prometheus should scrape metrics from and how often. Alerting rules define conditions that trigger alerts. Recording rules pre-compute frequently used expressions to improve query performance.
*   **Grafana Dashboards:** Customize existing dashboards or create your own to visualize the metrics that are most important to you.  Grafana supports a wide range of visualizations, including graphs, gauges, tables, and heatmaps. You can also use variables to make your dashboards more dynamic and reusable.

## Conclusion

Monitoring your Kubernetes clusters is crucial for ensuring application health, optimizing performance, and quickly resolving issues. Prometheus and Grafana provide a powerful and flexible solution for monitoring Kubernetes, offering a comprehensive set of features for collecting, storing, visualizing, and alerting on metrics. By following the steps outlined in this post, you can establish a robust monitoring system that empowers you to gain deeper insights into your Kubernetes environments and proactively address potential problems. Remember to continually refine your configurations and dashboards to adapt to the evolving needs of your applications and infrastructure.
