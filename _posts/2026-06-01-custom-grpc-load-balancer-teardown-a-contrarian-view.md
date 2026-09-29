---
layout: post
title: "Custom gRPC Load Balancer Teardown: A Contrarian View"
date: 2026-06-01 15:26:10 +0000
categories: [Distributed Systems, Reliability]
tags: [grpc, envoy, load-balancing]
description: This post dissects the operational complexities and hidden costs of a custom gRPC L7 load balancer, arguing for a migration to managed service proxies despite initial performance gains.
author: ritesh
cluster: "ai_code_in_production"
scenario: illustrative
---

Our `grpc_request_duration_p99` metric initially dropped by 15% across several critical services after deploying our custom L7 gRPC load balancer, seemingly validating our significant investment. However, the `mean_time_to_restore_service` for gRPC-related incidents simultaneously surged by an alarming 200% over the subsequent quarter, revealing a deeper, systemic cost to our platform's reliability.

## Chasing the Millisecond: Why We Built a Custom gRPC L7 Load Balancer

The impetus for building a custom L7 gRPC load balancer stemmed from a perceived inability of off-the-shelf solutions to meet our specific performance and routing requirements for a high-volume, stateful gRPC ecosystem. Standard L4 load balancers, while efficient for TCP, lacked the application-layer visibility needed for intelligent gRPC routing based on metadata, service versions, or user session affinity. Existing L7 proxies like vanilla Envoy or HAProxy, while capable of HTTP/2, often presented challenges with long-lived gRPC streams, particularly concerning connection draining, graceful restarts, and consistent load distribution across a dynamically scaling backend fleet. Our core objective was to achieve sub-millisecond latency improvements and precise control over traffic distribution that we believed was only possible with a bespoke solution tailored to our gRPC service mesh. This pursuit was driven by a genuine need to optimize resource utilization and enhance user experience in a latency-sensitive environment.

## Architectural Blueprint: Our Custom Envoy-based gRPC Proxy Design

Our custom gRPC load balancer was built around an Envoy proxy core, extended with custom filters and a bespoke control plane. The data plane leveraged Envoy's HTTP/2 capabilities, treating gRPC streams as multiplexed HTTP/2 requests. Key customizations included:

*   **Custom Envoy Filters**: We implemented a Lua filter to inspect gRPC `grpc-metadata` headers for routing decisions, enabling complex canary deployments and tenant-aware traffic steering. This filter would extract specific metadata (e.g., `x-tenant-id`, `x-service-version`) and modify the `x-envoy-upstream-alt-stat-name` header to influence upstream selection.
*   **Dynamic Control Plane**: A custom Go service served as the xDS server, dynamically configuring Envoy instances based on service discovery events from Kubernetes and an internal configuration store. This allowed for real-time updates to cluster membership, endpoint health, and routing rules.
*   **Connection Affinity Logic**: For specific stateful services, we developed a custom hashing algorithm within the control plane to ensure requests from a particular client or session were consistently routed to the same backend instance. This was implemented via `RING_HASH` load balancing with a custom hash policy derived from gRPC metadata.

Here's a simplified Envoy listener configuration snippet illustrating our custom filter chain:

```yaml
# Envoy Listener Configuration Snippet
listeners:
- name: listener_0
  address:
    socket_address:
      protocol: TCP
      address: 0.0.0.0
      port_value: 8080
  filter_chains:
  - filters:
    - name: envoy.filters.network.http_connection_manager
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
        stat_prefix: ingress_http
        route_config:
          name: local_route
          virtual_hosts:
          - name: backend_service
            domains: ["*"]
            routes:
            - match:
                prefix: "/"
              route:
                cluster: backend_service_cluster
                # Custom header for tenant-aware routing
                # Note: This is simplified; actual logic was in a Lua filter
                # which would set a dynamic cluster or modify metadata.
        http_filters:
        - name: envoy.filters.http.lua
          typed_config:
            "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
            inline_code: |
              function envoy_on_request(request_handle)
                local tenant_id = request_handle:headers():get("x-tenant-id")
                if tenant_id then
                  request_handle:logInfo("Routing for tenant: " .. tenant_id)
                  -- Example: Modify upstream cluster based on tenant_id
                  -- In reality, this would involve more complex logic or
                  -- setting a metadata key for a subsequent routing filter.
                  -- request_handle:headers():add("x-envoy-upstream-alt-stat-name", "backend_cluster_" .. tenant_id)
                end
              end
        - name: envoy.filters.http.router
          typed_config: {}
```

## The Hidden Tax: Unpacking Operational Complexity and Debugging Nightmares

While the custom load balancer delivered on its performance promises, it introduced an unforeseen level of operational complexity that quickly overshadowed any gains. Debugging became an order of magnitude harder. Standard tooling for network diagnostics, like `tcpdump` or `curl`, provided limited insight into gRPC stream states or the custom metadata routing logic. When an issue arose, engineers had to navigate not only Envoy's extensive configuration but also our custom xDS server logic, the custom Lua filters, and the intricate interactions between them.

Observability, initially robust for basic HTTP/2 metrics, became opaque for the custom routing decisions. Tracing required custom propagators to ensure `x-tenant-id` or other business-specific identifiers were carried through, and integrating these into existing distributed tracing systems (e.g., Jaeger, OpenTelemetry) was a continuous, manual effort. This led to prolonged incident resolution times, especially during critical production outages. The cognitive load on the on-call rotation significantly increased, as diagnosing a gRPC routing issue now required expertise spanning network protocols, Envoy internals, and our bespoke control plane. The cost of maintaining, patching, and upgrading this custom stack also grew disproportionately with each new Envoy release or Kubernetes version.

## Failure Modes: From Connection Draining Woes to Protocol Mismatches

Our custom gRPC load balancer, despite its sophistication, exhibited several critical failure modes under production load:

### Ungraceful Connection Draining

When backend services scaled down or were redeployed, the custom Envoy instances often failed to gracefully drain existing gRPC streams. While Envoy has built-in draining mechanisms, our custom routing logic, combined with long-lived gRPC streams (e.g., bidirectional streaming for real-time updates), created scenarios where `drain_timeout` was insufficient. Clients would experience `UNAVAILABLE` errors or abrupt stream terminations, leading to application-level retries and increased upstream load. This was particularly evident when `SIGTERM` signals were not properly handled by our custom control plane in conjunction with Envoy's hot restart capabilities, leading to dropped connections rather than smooth transitions.

```log
# Example log snippet from an affected client
2023-10-26T14:35:12Z grpc: RPC failed with status code Unavailable and message "upstream connect error or disconnect/reset before headers. reset reason: connection termination"
```

### Protocol Mismatches and Interoperability Issues

As the gRPC ecosystem evolved, new features or subtle changes in protocol semantics occasionally exposed incompatibilities with our custom filters or control plane logic. For instance, specific gRPC health checking patterns or advanced flow control mechanisms in newer gRPC client libraries sometimes interacted unexpectedly with our custom Envoy configuration, leading to intermittent connection resets or perceived backend unresponsiveness. Diagnosing these required deep packet inspection and cross-referencing gRPC specification changes against our custom implementation, a process that was both time-consuming and prone to human error.

### Resource Exhaustion Under High Fan-out

While optimized for latency, our custom control plane struggled with resource exhaustion when managing a very large number of dynamically changing backend services. The xDS server, responsible for generating and pushing Envoy configurations, would occasionally experience CPU spikes and increased memory usage, leading to delays in configuration propagation. This meant that new backend instances might not receive traffic for several minutes, or unhealthy instances might not be removed promptly, leading to cascading failures.

## The Migration Path: Phased Rollout to a Managed Service Proxy

Recognizing the unsustainable operational overhead, we initiated a phased migration away from our custom gRPC load balancer towards a managed service mesh solution (specifically, a cloud provider's managed Envoy offering). The migration strategy focused on minimizing blast radius and ensuring service continuity:

1.  **Traffic Shadowing**: Initially, a small percentage of production traffic was shadowed to the new managed proxy environment. This involved duplicating requests at the custom LB and sending them to both the old and new paths, with only the old path's response being returned to the client. This allowed us to validate the new proxy's behavior without impacting users.
2.  **Canary Rollout**: Once shadowing proved stable, a small percentage (e.g., 1-5%) of live traffic was gradually shifted to the managed proxy. This was carefully monitored using golden signals (latency, error rates, throughput, saturation) for both the proxy and the downstream services.
3.  **Feature Parity Mapping**: Our custom routing logic (e.g., tenant-based routing, canary deployments) was meticulously re-implemented using the managed proxy's native capabilities or standard Envoy features. For example, custom Lua filters were replaced with Envoy's `match` conditions on `grpc_metadata_match` or `header_match` within `RouteConfiguration`.
    ```yaml
    # Example: Replaced custom Lua with native Envoy header matching
    # for tenant-based routing in the managed proxy setup.
    route:
      cluster: backend_service_cluster
      typed_per_filter_config:
        envoy.filters.http.router:
          "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.RouterPerRoute
          cluster_header: "x-tenant-upstream-cluster" # Set by a preceding filter or derived from route match
    match:
      prefix: "/my.TenantService/"
      grpc_metadata_match:
        - name: "x-tenant-id"
          exact_match: "tenantA"
    ```
4.  **Iterative A/B Testing**: Each significant traffic shift involved A/B testing key performance indicators and error rates between the custom LB path and the new managed proxy path. This iterative approach allowed for quick rollback if any regressions were detected.
5.  **Decommissioning**: After all traffic was successfully migrated and stabilized, the custom load balancer instances and their control plane components were systematically decommissioned, freeing up significant operational resources.

This migration validated that the perceived necessity for a custom solution was largely an artifact of an earlier ecosystem state. Modern managed proxies and service meshes have evolved to provide robust, configurable gRPC support that often surpasses the operational capabilities of a bespoke system.

## Operational Checklist: Evaluating Your Need for a Custom gRPC LB

Before embarking on building a custom gRPC L7 load balancer, critically evaluate these points:

*   **Can existing L7 proxies (Envoy, Linkerd, Istio) meet your requirements via configuration?** Explore their `RouteConfiguration`, `VirtualService`, `Gateway` resources, and advanced filter options.
*   **Are your "unique" routing needs truly unique, or can they be mapped to standard gRPC metadata-based routing or header matching?** Often, a simpler approach exists.
*   **What is the total cost of ownership (TCO) including development, maintenance, debugging, and on-call burden?** Factor in engineer hours, not just infrastructure costs.
*   **How will you manage upgrades and patches for your custom stack?** Will it keep pace with upstream gRPC and proxy developments?
*   **What is your observability strategy for custom routing logic?** Can your existing tracing and logging infrastructure easily integrate with bespoke filters?
*   **How will you handle graceful connection draining and restarts for long-lived gRPC streams in your custom setup?** This is a common pitfall.
*   **Do you have dedicated platform engineering resources to maintain this specialized infrastructure long-term?** This is not a "set it and forget it" component.
*   **What is your rollback strategy if the custom solution introduces more problems than it solves?**

## Signals to watch

If you run (or are considering) a custom gRPC load balancer, these are the signals that show whether it is paying for itself:

*   `grpc_request_duration_p99`: whether the custom layer actually improves tail latency.
*   Mean time to restore service for gRPC-related incidents: the operational cost of owning the load balancer.
*   `envoy_cluster_upstream_rq_timeout`: spikes during load-balancer draining events.
*   Client-side `UNAVAILABLE` errors: correlation with load-balancer restarts or backend scaling events.
*   Custom xDS server CPU and memory: spikes during high-churn service discovery.

## References

*   **Platform Vendor References**:
    *   Google Cloud Load Balancing, [gRPC support in the External Application Load Balancer](https://docs.cloud.google.com/load-balancing/docs/https#grpc-support) (Example of managed solution capabilities)
    *   AWS App Mesh for gRPC: [https://aws.amazon.com/app-mesh/](https://aws.amazon.com/app-mesh/) (Another managed option leveraging Envoy)
*   **Official Docs**:
    *   Envoy Proxy HTTP/2 Configuration: [https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/route/v3/Route.proto](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/route/v3/Route.proto) (Details on `grpc_metadata_match` and routing options)
    *   gRPC Health Checking Protocol: [https://github.com/grpc/grpc/blob/master/doc/health-checking.md](https://github.com/grpc/grpc/blob/master/doc/health-checking.md) (Understanding standard health check mechanisms)

### Related
- [Fixing Performance Bottlenecks in AI-Assisted Code Reviews Due to Excessive API Call Volume](/posts/fixing-performance-bottlenecks-in-ai-assisted-code-reviews-due-to-excessive-api-call-volume/)
- [Debugging Agentic AI Code Generation Loops in Kubernetes](/posts/debugging-agentic-ai-code-generation-loops-in-kubernetes/)
- [Fixing Abrupt Pod Terminations: Implementing Graceful Shutdown in AI-Assisted Python Services on Kubernetes](/posts/fixing-abrupt-pod-terminations-implementing-graceful-shutdown-in-ai-assisted-python-services-on-kubernetes/)
- [Primary Source](https://platform.openai.com/docs/guides/production-best-practices)
- [Primary Source](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
