---
layout: post
title: "Refactoring AI-Generated Python Services for Production Reliability on Kubernetes"
date: 2026-03-16 10:07:28 +0000
categories: [Kubernetes, Python, AI-Assisted Development]
tags: [python, kubernetes, refactoring, production-readiness, ai-code, distributed-systems]
---

We've been cautiously experimenting with AI-assisted code generation for a few months, specifically to accelerate development of non-critical internal tools and prototypes. The promise of quickly standing up services from high-level requirements is tempting. However, a recent incident highlighted a critical gap: while AI can generate functional code, it often lacks the architectural rigor and operational awareness required for robust distributed systems in production Kubernetes environments.

Our platform engineering team was paged last week by repeated alerts from a new internal data processing service, `ai-processor-v1`, deployed on one of our development clusters. This service was responsible for ingesting large CSV files, performing some light transformation, and writing data to a PostgreSQL instance. It was one of the first services where a significant portion of the Python business logic had been primarily "AI-authored" and then quickly reviewed and deployed.

Initially, `ai-processor-v1` seemed fine. It processed small files without issue. But once subjected to larger, more frequent payloads, its behavior became erratic. We observed high latency, frequent `HTTP 500` errors from downstream APIs that `ai-processor-v1` called, and then eventually, `CrashLoopBackOff` events for the pods themselves. The Kubernetes HPA was frantically trying to scale up, creating new pods that would also eventually fail.

```bash
$ kubectl get pods -l app=ai-processor-v1
NAME                             READY   STATUS             RESTARTS   AGE
ai-processor-v1-abcdef-ghijk     0/1     CrashLoopBackOff   5          15m
ai-processor-v1-abcdef-lmno     0/1     CrashLoopBackOff   4          12m
ai-processor-v1-abcdef-pqrs     1/1     Running            0          1m
... (many more pods, some running, some crashing)
```

Inspecting logs from a crashing pod revealed an unhelpful stream of generic errors:

```bash
$ kubectl logs ai-processor-v1-abcdef-ghijk
...
ERROR:root:Error processing batch: Request timed out
ERROR:root:Database operation failed: could not connect to server: Connection refused
...
Traceback (most recent call last):
  File "/app/main.py", line 123, in process_data
    response = requests.post(downstream_api_url, json=data_chunk)
  File "/usr/local/lib/python3.10/site-packages/requests/api.py", line 117, in post
    return request('post', url, data=data, json=json, **kwargs)
  File "/usr/local/lib/python3.10/site-packages/requests/api.py", line 61, in request
    return session.request(method=method, url=url, **kwargs)
  File "/usr/local/lib/python3.10/site-packages/requests/sessions.py", line 529, in request
    resp = self.send(prep, **send_kwargs)
  File "/usr/local/lib/python3.10/site-packages/requests/sessions.py", line 643, in send
    r = adapter.send(request, **kwargs)
  File "/usr/local/lib/python3.10/site-packages/requests/adapters.py", line 532, in send
    raise ConnectTimeout(e, request=request)
requests.exceptions.ConnectTimeout: HTTPSConnectionPool(host='downstream-api', port=443): Max retries exceeded with url: /data (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x...>, 'Connection to downstream-api timed out. (connect timeout=5)'))
...
```

The `requests.exceptions.ConnectTimeout` and `Database operation failed: could not connect` messages were particularly alarming, given that the downstream API and PostgreSQL database were healthy and serving other services without issue. This pointed to `ai-processor-v1` itself being the source of its own demise, likely through resource exhaustion or blocking I/O.

### The Root Cause: Synchronous Blocking I/O and Poor Resource Management

Upon reviewing the AI-generated Python code, the problem became painfully clear. While functionally correct for small-scale operations, the service's core processing loop was a textbook example of how *not* to handle concurrent I/O in Python:

```python
# ai-processor-v1/app/main.py (Simplified, problematic AI-generated snippet)

import requests
import psycopg2
import time
from concurrent.futures import ThreadPoolExecutor

# ... (connection details for DB and downstream API)

def process_chunk_sync(chunk_data):
    """Processes a single data chunk synchronously."""
    try:
        # Simulate CPU-bound work
        time.sleep(0.01)

        # Blocking HTTP call to downstream API
        response = requests.post(DOWNSTREAM_API_URL, json=chunk_data.to_dict(), timeout=5)
        response.raise_for_status()

        # Blocking DB write
        with DB_CONNECTION_POOL.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO processed_data (id, payload) VALUES (%s, %s)",
                               (chunk_data.id, response.json()))
            conn.commit()
        DB_CONNECTION_POOL.putconn(conn)
        return True
    except (requests.exceptions.RequestException, psycopg2.Error) as e:
        print(f"ERROR: Error processing chunk: {e}")
        return False

@app.route('/process', methods=['POST'])
def handle_upload():
    # ... (file parsing logic)
    data_chunks = parse_csv_to_chunks(request.data)

    # Problem: Using ThreadPoolExecutor, but 'requests' and 'psycopg2' are blocking
    # Python's GIL means CPU-bound threads don't truly run in parallel.
    # For I/O-bound tasks, it still works by releasing GIL during I/O,
    # but the number of threads must be managed carefully.
    # The default ThreadPoolExecutor size can quickly exhaust resources if not tuned.
    results = []
    with ThreadPoolExecutor() as executor: # Default max_workers depends on CPU cores, often 5*CPU_COUNT
        futures = [executor.submit(process_chunk_sync, chunk) for chunk in data_chunks]
        for future in futures:
            results.append(future.result()) # This blocks the main thread waiting for results

    # ... (response generation)
```

The AI's logic was to use `ThreadPoolExecutor` for concurrency, which is a common pattern. However, it failed to account for several critical points in a high-throughput, I/O-bound service:

1.  **Blocking `requests` and `psycopg2`**: Both libraries are inherently blocking. While `ThreadPoolExecutor` helps by running these in separate threads, Python's Global Interpreter Lock (GIL) means true CPU-bound parallelism is limited. More importantly, for I/O-bound tasks, creating hundreds or thousands of threads (as implied by processing `data_chunks` rapidly without proper batching or limiting `max_workers`) leads to massive context switching overhead and memory consumption. Each thread requires its own stack and kernel resources.
2.  **Unbounded Concurrency**: The `ThreadPoolExecutor()` was instantiated without `max_workers`, defaulting to a value typically 5 times the number of CPU cores. When hit with a large file parsed into hundreds or thousands of `data_chunks`, it would attempt to spawn an equivalent number of threads, far exceeding safe operating limits for the pod's resources.
3.  **Connection Pool Exhaustion**: While `psycopg2` `DB_CONNECTION_POOL` was used, the sheer number of concurrent blocking requests quickly exhausted the pool, leading to `Connection refused` errors.
4.  **Resource Limits Exceeded**: With hundreds of threads trying to perform I/O and holding memory, the pod rapidly consumed its allocated memory, leading to Kubernetes terminating it with an `OOMKilled` event. The HPA would then try to scale up, but new pods would just repeat the cycle.

```yaml
# Problematic Kubernetes Deployment for ai-processor-v1
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-processor-v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-processor-v1
  template:
    metadata:
      labels:
        app: ai-processor-v1
    spec:
      containers:
      - name: processor
        image: myregistry/ai-processor-v1:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi" # This limit was too low for unbounded threading
            cpu: "500m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-processor-v1-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-processor-v1
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

The HPA was reacting to CPU utilization, but the primary issue was memory exhaustion due to excessive thread creation and blocking I/O, leading to a death spiral.

### Refactoring for Stability: Embracing Asynchronous I/O

The solution was a targeted refactor to leverage Python's `asyncio` for non-blocking I/O, which is far more efficient for services making numerous concurrent network and database calls. This fundamentally changes how the service utilizes system resources, allowing a single event loop to manage thousands of concurrent I/O operations without spawning a thread per operation.

We chose to use `aiohttp` for asynchronous HTTP requests and `asyncpg` for asynchronous PostgreSQL interactions.

```python
# ai-processor-v1/app/main.py (Refactored for Asyncio)

import asyncio
import aiohttp
import asyncpg # Requires 'asyncpg' library
import time
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ... (connection details, env vars for DB and downstream API)
DOWNSTREAM_API_URL = os.getenv("DOWNSTREAM_API_URL", "http://downstream-api/data")
DB_HOST = os.getenv("DB_HOST", "db-service")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "database")

# Global connection pool for asyncpg
db_pool = None

async def init_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            user=DB_USER, password=DB_PASSWORD,
            host=DB_HOST, port=DB_PORT,
            database=DB_NAME,
            min_size=5, max_size=20 # Tuned for expected concurrency
        )
    return db_pool

async def process_chunk_async(session: aiohttp.ClientSession, chunk_data):
    """Processes a single data chunk asynchronously."""
    try:
        # Simulate CPU-bound work (use run_in_executor for heavy CPU tasks if needed)
        # await asyncio.sleep(0.01) # Small non-blocking delay example

        # Non-blocking HTTP call
        async with session.post(DOWNSTREAM_API_URL, json=chunk_data.to_dict(), timeout=aiohttp.ClientTimeout(total=5)) as response:
            response.raise_for_status()
            api_response_json = await response.json()

        # Non-blocking DB write
        pool = await init_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("INSERT INTO processed_data (id, payload) VALUES ($1, $2)",
                               chunk_data.id, api_response_json)
        return True
    except (aiohttp.ClientError, asyncpg.PostgresError) as e:
        logger.error(f"Error processing chunk {chunk_data.id}: {e}")
        return False

# Example FastAPI app using Uvicorn (async-native web server)
from fastapi import FastAPI, Request, HTTPException
import pandas as pd
import io

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db_pool()
    logger.info("Database connection pool initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    if db_pool:
        await db_pool.close()
        logger.info("Database connection pool closed.")

@app.post('/process')
async def handle_upload(request: Request):
    try:
        data = await request.body()
        df = pd.read_csv(io.BytesIO(data))
        data_chunks = [row.to_dict() for index, row in df.iterrows()] # Simplified for example

        results = []
        async with aiohttp.ClientSession() as session:
            # Concurrently process chunks with a controlled degree of parallelism
            # Limit parallelism to avoid overwhelming downstream services or local resources
            # We use asyncio.Semaphore to limit concurrent tasks
            sem = asyncio.Semaphore(20) # Max 20 concurrent tasks

            async def bounded_process(chunk):
                async with sem:
                    return await process_chunk_async(session, chunk)

            tasks = [bounded_process(chunk) for chunk in data_chunks]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_chunks = [r for r in results if r is True]
        failed_chunks = [r for r in results if r is not True] # Includes Exceptions

        if failed_chunks:
            logger.warning(f"Processed {len(successful_chunks)} chunks, {len(failed_chunks)} failed.")
            raise HTTPException(status_code=500, detail="Some chunks failed processing.")
        
        logger.info(f"Successfully processed {len(successful_chunks)} chunks.")
        return {"status": "success", "processed_chunks": len(successful_chunks)}
    except Exception as e:
        logger.error(f"Failed to handle upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")

# To run this with Uvicorn: uvicorn main:app --host 0.0.0.0 --port 8000
```

Key changes implemented:
1.  **`asyncio` Core**: The entire service now runs on an `asyncio` event loop.
2.  **`FastAPI` and `Uvicorn`**: Replaced generic Flask setup with `FastAPI` and `Uvicorn`, which are async-native, ensuring the web server itself doesn't block.
3.  **`aiohttp` for HTTP**: Used `aiohttp.ClientSession` for non-blocking HTTP requests. A single session can be reused for many requests, reducing overhead.
4.  **`asyncpg` for PostgreSQL**: Switched to `asyncpg` for non-blocking database operations, with a properly configured connection pool.
5.  **Controlled Concurrency with `asyncio.Semaphore`**: Instead of unbounded thread creation, we now explicitly limit the number of *concurrent asynchronous tasks* using `asyncio.Semaphore`. This prevents resource exhaustion and provides graceful backpressure to upstream systems if the service is overloaded. `asyncio.gather` efficiently waits for all tasks.
6.  **Startup/Shutdown Hooks**: `FastAPI`'s `on_event` handlers manage the asyncpg connection pool lifecycle properly.

### Kubernetes Configuration Adjustments

With the Python service now efficiently handling I/O, we could tune the Kubernetes resource requests and limits more effectively. The service now uses CPU more consistently and memory far more predictably.

```yaml
# Updated Kubernetes Deployment for ai-processor-v1
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-processor-v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-processor-v1
  template:
    metadata:
      labels:
        app: ai-processor-v1
    spec:
      containers:
      - name: processor
        image: myregistry/ai-processor-v1:v2-async
        ports:
        - containerPort: 8000 # Uvicorn default port
        resources:
          requests:
            memory: "128Mi" # Lower memory request due to async efficiency
            cpu: "200m"
          limits:
            memory: "256Mi" # Tighter, more predictable memory limit
            cpu: "750m"
        envFrom: # Use envFrom for better secret/config management
        - configMapRef:
            name: ai-processor-config
        - secretRef:
            name: ai-processor-secrets
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-processor-v1-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-processor-v1
  minReplicas: 3
  maxReplicas: 15 # Increased max replicas as pods are now more efficient
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Resource # Add memory metric for better scaling decisions
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
```

We also added a `memory` metric to the HPA to provide more robust autoscaling based on both CPU and memory utilization, preventing `OOMKilled` incidents even under extreme load.

### Post-Refactor Stability

After deploying the refactored `ai-processor-v1` service, the difference was immediate and significant:
*   **Stable Resource Utilization**: Pods now maintain stable CPU and memory profiles, even under high load.
*   **Reduced Latency**: Average processing time for batches dropped by 80%.
*   **No `OOMKilled` or `CrashLoopBackOff`**: The service now scales gracefully without intermittent failures.
*   **Improved Observability**: With cleaner code and proper error handling, logs are far more informative.

This experience underscores that while AI can rapidly generate functional code, its current capabilities often fall short of producing production-ready distributed system components. The "easy" solutions provided by AI frequently overlook critical aspects like concurrent I/O patterns, robust error handling, and efficient resource management – precisely the areas that differentiate a prototype from a stable, scalable production service.

Human engineers remain essential for applying architectural judgment, understanding system-wide implications, and ensuring the operational resilience of these components, especially in complex environments like Kubernetes. Our role is evolving from writing every line of code to becoming expert architects and refactorers, shaping and hardening AI-generated foundations into battle-tested systems.
