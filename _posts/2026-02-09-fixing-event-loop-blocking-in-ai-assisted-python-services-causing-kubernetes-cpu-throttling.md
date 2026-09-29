---
layout: post
title: "Fixing Event Loop Blocking in AI-Assisted Python Services Causing Kubernetes CPU Throttling"
date: 2026-02-09 09:00:00 +0000
categories: [AI, Python]
tags: [code-quality, event-loop, cpu-throttling, asyncio, debugging, performance, microservices]
description: "How synchronous calls inside async handlers caused CPU throttling in Kubernetes pods and the fix using proper asyncio patterns and process pool executors."
author: ritesh
scenario: illustrative
---

We recently encountered a recurring issue with a newly deployed data aggregation microservice in our Kubernetes cluster. The service, written in Python with FastAPI, had its core data processing and external API interaction logic heavily assisted by AI code generation. Initial development and local testing were rapid, and the service passed basic integration tests in staging environments. However, once deployed to production, we began seeing intermittent, severe latency spikes, followed by `CrashLoopBackOff` events for its pods during specific peak traffic windows.

Our platform engineering team was paged frequently. The symptom was consistent: a sudden degradation in response times, then pods failing their `readinessProbe` or being `OOMKilled` or `Terminated` by Kubernetes, [triggering a restart loop](/posts/troubleshooting-crashloopbackoff-errors/).

Initial investigation using standard Kubernetes tooling revealed a pattern:

```bash
# Check pod status and restart counts
kubectl get pods -n data-services -l app=data-aggregator
NAME                                    READY   STATUS             RESTARTS   AGE
data-aggregator-789c74d6f8-abcde        1/1     Running            2          3h
data-aggregator-789c74d6f8-fghij        0/1     CrashLoopBackOff   5          2h55m

# Describe a failing pod
kubectl describe pod data-aggregator-789c74d6f8-fghij -n data-services
# ...
Events:
  Type     Reason     Age                  From               Message
  ----     ------     ----                 ----               -------
  Warning  Unhealthy  2m (x5 over 2h50m)   kubelet            Liveness probe failed: HTTP GET http://10.244.1.10:8000/health timed out
  Warning  BackOff    1m (x5 over 2h50m)   kubelet            Back-off restarting failed container
  Normal   Pulled     30s (x6 over 2h55m)  kubelet            Container image "data-aggregator:1.0.0" already present on machine
  Normal   Created    30s (x6 over 2h55m)  kubelet            Created container data-aggregator
  Normal   Started    30s (x6 over 2h55m)  kubelet            Started container data-aggregator
  Warning  Killing    30s (x5 over 2h50m)  kubelet            Container data-aggregator failed liveness probe, is restarting
```

During incident periods, `kubectl top pod` showed an alarming trend:

```bash
# Check resource usage during an incident
kubectl top pod data-aggregator-789c74d6f8-abcde -n data-services
NAME                           CPU(cores)   MEMORY(bytes)
data-aggregator-789c74d6f8-abcde   1050m        250Mi
```

Our `data-aggregator` deployment had a CPU request of `500m` and a limit of `1000m` (1 full core). Observing CPU usage spiking above `1000m` (e.g., `1050m`) was a clear indicator of CPU throttling. Kubernetes was actively restricting the pod's CPU time, leading to performance degradation and eventually liveness probe failures due to timeouts.

Further investigation into Prometheus metrics from `kube-state-metrics` confirmed the throttling:

```promql
# Example PromQL query to observe CPU throttled periods for the affected pods
sum(rate(container_cpu_cfs_throttled_periods_total{namespace="data-services", pod=~"data-aggregator.*"}[5m])) by (pod)
```

This metric showed significant throttled periods correlating precisely with the latency spikes. The application was consistently trying to consume more CPU than its `limits` allowed.

The core question became: *Why* was a relatively simple Python service with ostensibly low CPU requirements suddenly hammering the CPU to this extent?

Given the context of AI-assisted development, a common anti-pattern immediately came to mind for Python `asyncio` services: blocking I/O calls within an `async` context. AI models, while excellent at boilerplate, often generate synchronous code patterns by default or without a deep understanding of the surrounding asynchronous framework's implications.

We extracted the problematic service image and ran it locally, simulating production load using `locust`. We then used `py-spy` to profile the running process:

```bash
# Install py-spy in a development environment or locally if permitted
pip install py-spy

# Profile a running uvicorn process (replace PID with actual process ID)
# Example: py-spy record -o profile.svg --pid $(pgrep uvicorn)
py-spy record -o profile.svg --pid 12345 --duration 30
```

The `profile.svg` flame graph was illuminating. A significant portion of the CPU time was spent deep within a `requests.Session().get()` call, which was executed directly inside one of our FastAPI `async def` endpoints:

```python
# app/api/endpoints.py (AI-generated snippet)
import requests
from fastapi import APIRouter, HTTPException

router = APIRouter()
# AI often generates global sessions for convenience without async considerations
session = requests.Session() 

@router.get("/aggregate/{item_id}")
async def get_aggregated_data(item_id: str):
    try:
        # AI-generated external call
        # requests.Session().get() is a synchronous call!
        response = session.get(f"http://external-api.com/data/{item_id}", timeout=5)
        response.raise_for_status()
        external_data = response.json()

        # ... further asynchronous processing ...
        return {"item_id": item_id, "data": external_data}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"External API error: {e}")
```

This was the culprit. The `requests` library is synchronous. When `session.get()` is called within an `async def` function, it *blocks the entire `asyncio` event loop* until the HTTP request completes. In a highly concurrent web service like FastAPI, this means *all other pending requests and tasks* are stalled while one single request is waiting for the external API. This causes the event loop to become saturated, CPU utilization to skyrocket as `asyncio` tries to manage the backlog, and overall latency to increase dramatically. Our `livenessProbe` was timing out because the event loop was too busy processing pending tasks to respond to the health check endpoint.

The fix involved refactoring the problematic code to use [an asynchronous HTTP client](/posts/boosting-python-performance-with-asynchronous-programming-and-asyncio/), `httpx`, which is fully compatible with `asyncio`.

First, update dependencies in `pyproject.toml` (or `requirements.txt`):

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.110.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
httpx = "^0.27.0" # New dependency for async HTTP
```

Then, modify the service code to use `httpx.AsyncClient` and handle its lifecycle:

```python
# app/api/endpoints.py (Refactored)
import httpx # Changed import
from fastapi import APIRouter, HTTPException
from contextlib import asynccontextmanager

router = APIRouter()

# Manage httpx.AsyncClient lifecycle using FastAPI's lifespan events
# This ensures the client is properly initialized and closed.
@asynccontextmanager
async def lifespan(app: FastAPI):
    global async_client
    async_client = httpx.AsyncClient(timeout=5.0)
    yield
    await async_client.aclose()

# Use this lifespan context manager with your FastAPI app instance:
# app = FastAPI(lifespan=lifespan)

@router.get("/aggregate/{item_id}")
async def get_aggregated_data(item_id: str):
    try:
        # Use the asynchronous client and await the call
        response = await async_client.get(f"http://external-api.com/data/{item_id}")
        response.raise_for_status()
        external_data = response.json()

        # ... further asynchronous processing ...
        return {"item_id": item_id, "data": external_data}
    except httpx.RequestError as e: # Catch httpx specific exceptions
        raise HTTPException(status_code=500, detail=f"External API error: {e}")

# In a real application, ensure the 'async_client' is accessible
# For simple cases, you might initialize it directly, but dependency injection
# or lifespan events are preferred for robustness.
```

After deploying the refactored service, the results were immediate and positive. CPU usage normalized, `container_cpu_cfs_throttled_periods_total` dropped to zero, and the erratic latency spikes disappeared. Pods remained stable without restarts.

**Key Takeaways:**

1.  **AI-Generated Code Requires Scrutiny:** While AI tools accelerate development, their output, especially for complex asynchronous systems, demands thorough review and profiling. They may lack the contextual awareness to prevent subtle performance anti-patterns like blocking I/O within an `asyncio` event loop.
2.  **Asynchronous I/O is Critical:** In Python's `asyncio` ecosystem, any blocking I/O (file operations, synchronous HTTP calls, traditional database drivers) within an `async def` function will stall the entire event loop, severely impacting concurrency and performance. Tools like `py-spy` are indispensable for identifying these bottlenecks.
3.  **Monitor CPU Throttling:** `container_cpu_cfs_throttled_periods_total` is an invaluable metric in Kubernetes for identifying applications that are bottlenecked by CPU limits. High throttling often indicates inefficient code or misconfigured resources, not necessarily just "not enough CPU."
4.  **Robust Probes:** Our `livenessProbe` was too simplistic. A more robust probe might involve checking the `asyncio` event loop's backlog or processing time to proactively detect stalls before a hard timeout.
5.  **Right-Sizing Resources:** [Kubernetes resource requests and limits](/posts/kubernetes-resource-requests-and-limits-masterclass/) should be based on actual application profiling under realistic load, not just guesswork or initial development-phase observations. While the AI-generated code was the root cause here, correctly sized resources could have provided more headroom before catastrophic failure, but would not have solved the underlying inefficiency.
