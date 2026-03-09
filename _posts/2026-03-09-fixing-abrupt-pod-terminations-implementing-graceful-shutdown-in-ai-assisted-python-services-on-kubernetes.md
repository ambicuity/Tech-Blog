---
layout: post
title: "Fixing Abrupt Pod Terminations: Implementing Graceful Shutdown in AI-Assisted Python Services on Kubernetes"
date: 2026-03-09 09:54:01 +0000
categories: [distributed-systems, kubernetes, python]
tags: [graceful-shutdown, sigterm, kubernetes, python, microservices, reliability, platform-engineering, production-readiness]
---

Recently, our team adopted AI assistance for boilerplate code generation, particularly for new microservices. The `payment-processor-v2` service, a Python Flask application, was one such candidate. The AI model provided an almost perfect Flask blueprint, complete with SQLAlchemy models, basic validation, and RESTful endpoints. It nailed the business logic, reducing development time significantly. Initial local testing and even low-load staging deployments looked promising.

However, the real world quickly surfaced a subtle but critical production gap. During our first high-traffic rollout and subsequent scaling events on Kubernetes, we started seeing an uptick in `5xx` errors during deployments and an alarming number of incomplete payment transactions.

Upon inspection of the deployment events, we noticed pods transitioning to `Terminating` status and then abruptly disappearing. Kubernetes logs for the terminating pods often showed messages similar to this:

```
I0308 14:35:10.123456    1 controller.go:1234] Successfully killed container "payment-processor-v2" in pod "payment-processor-v2-xyz-abc" (UID: 123456)
```

Simultaneously, our application logs within these terminated pods would just stop mid-operation, without any clean shutdown messages. For example:

```
INFO:app:Received payment request for ID: PAY-20260308-001
INFO:app:Initiating external payment gateway call for PAY-20260308-001...
# ... (logs abruptly end here, no success or failure of the gateway call)
```

This indicated an abrupt termination. The service was not gracefully shutting down, meaning any in-flight requests or ongoing background tasks were being unceremoniously cut short. This is a classic symptom of an application failing to handle `SIGTERM` signals, which Kubernetes sends to pods to signal their impending termination.

The core issue was that while the AI generated functional code, it overlooked the operational robustness required for a high-availability, containerized environment. The generated Flask application simply ran with `python app.py` or a basic `gunicorn app:app` command, neither of which inherently provide comprehensive graceful shutdown mechanisms for arbitrary long-running tasks within the application itself without explicit configuration or code.

To fix this, we needed to ensure our Python service could gracefully complete ongoing work when Kubernetes sends a `SIGTERM` signal, preventing data loss and enhancing service reliability during deployments and scaling.

### Implementing Graceful Shutdown in the Python Application

The first step was to modify the Python application to actively listen for and respond to `SIGTERM`. This involves using Python's `signal` module to register a handler that, upon receiving `SIGTERM`, can initiate a controlled shutdown sequence.

Our `payment-processor-v2` service was primarily a Flask application. Here's how we augmented it to handle `SIGTERM`:

```python
import os
import signal
import sys
import threading
import time
from flask import Flask, request, jsonify

app = Flask(__name__)
# A simple flag to indicate if the service is shutting down
shutting_down = threading.Event()

def mock_external_api_call(payment_id):
    """Simulates a blocking, long-running external API call."""
    # In a real application, this would be an actual API call, DB write, etc.
    time.sleep(5) # Simulate 5 seconds of work
    return {"status": "success", "payment_id": payment_id}

@app.route('/process_payment', methods=['POST'])
def process_payment():
    # If the shutdown flag is set, reject new requests immediately
    if shutting_down.is_set():
        app.logger.warning("Service is shutting down, rejecting new payment request.")
        return jsonify({"message": "Service unavailable due to shutdown"}), 503

    payment_data = request.json
    payment_id = payment_data.get("id")
    app.logger.info(f"Received payment request for ID: {payment_id}")

    try:
        # Simulate business logic that might take time
        app.logger.info(f"Initiating external payment gateway call for {payment_id}...")
        result = mock_external_api_call(payment_id)
        app.logger.info(f"Payment {payment_id} processed: {result['status']}")
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Error processing payment {payment_id}: {e}", exc_info=True)
        return jsonify({"status": "failed", "error": str(e)}), 500

@app.route('/ready', methods=['GET'])
def ready_check():
    """Readiness probe endpoint. Reports NOT_READY during shutdown."""
    if shutting_down.is_set():
        return jsonify({"status": "NOT_READY", "reason": "shutting down"}), 503
    return jsonify({"status": "READY"}), 200

@app.route('/healthz', methods=['GET'])
def health_check():
    """Liveness probe endpoint. Reports HEALTHY unless critical issues."""
    return jsonify({"status": "HEALTHY"}), 200

def signal_handler(signum, frame):
    """
    Handles OS signals, specifically SIGTERM, for graceful shutdown.
    Sets the shutdown flag to stop accepting new requests.
    """
    app.logger.warning(f"Received signal {signum}. Initiating graceful shutdown...")
    shutting_down.set() # Set the flag to stop accepting new requests
    # In a real application, you might also:
    # - Close database connections
    # - Flush outstanding metrics/logs
    # - Notify external systems of impending shutdown
    app.logger.info("Graceful shutdown initiated. Waiting for active requests to complete.")
    # For a Gunicorn/Uvicorn managed app, the server itself handles worker graceful exits
    # after this signal is processed.

# Register the signal handler for SIGTERM
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    # This block is typically for local development or if running directly.
    # In production, Gunicorn/Uvicorn is preferred for managing workers.
    app.run(host='0.0.0.0', port=8000)

```

In this revised `app.py`:
*   We use a `threading.Event` (`shutting_down`) as a simple flag. When `SIGTERM` is received, `signal_handler` sets this event.
*   The `/process_payment` endpoint checks this flag. If `shutting_down` is set, it immediately rejects new requests with a `503 Service Unavailable` status, allowing the load balancer to route traffic away from the terminating pod.
*   Existing requests that started *before* `shutting_down` was set are allowed to complete their `mock_external_api_call` (simulating actual work).
*   A `/ready` endpoint is added. This probe will report `503 NOT_READY` when `shutting_down` is set, informing Kubernetes to stop routing new traffic to this pod.

While application-level signal handling is crucial, for Python web services in production, we rarely run `app.py` directly. Instead, a production-ready WSGI/ASGI server like Gunicorn is used to manage workers. Gunicorn itself has robust `SIGTERM` handling, propagating it to workers and respecting graceful timeouts.

Our `Dockerfile` was updated to use Gunicorn:

```dockerfile
# Dockerfile
FROM python:3.10-slim-bullseye

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir gunicorn flask

# Copy application code
COPY . .

# Expose the port our app runs on
EXPOSE 8000

# Command to run the application with Gunicorn
# --workers: Number of worker processes (tune based on CPU/RAM)
# --bind: Listen address
# --graceful-timeout: How long to wait for workers to finish current requests before forceful kill.
#                     This works in conjunction with SIGTERM handling within the app.
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "--graceful-timeout", "30", "app:app"]
```

Here, `gunicorn` orchestrates much of the `SIGTERM` handling. When Gunicorn receives `SIGTERM`, it sends `SIGTERM` to its child workers. Each worker (running our Flask app) then receives the signal, sets the `shutting_down` flag, stops accepting new requests, and finishes its current tasks. The `graceful-timeout` parameter in Gunicorn (`--graceful-timeout 30`) tells Gunicorn to wait up to 30 seconds for its workers to finish their requests before forcefully killing them. This works in concert with our application-level `shutting_down` flag.

### Configuring Kubernetes for Graceful Termination

Finally, to give our service ample time to shut down, we adjusted the `terminationGracePeriodSeconds` in our Kubernetes Deployment manifest. This parameter specifies how long Kubernetes should wait after sending a `SIGTERM` before sending a `SIGKILL` (which cannot be caught by the application).

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-processor-v2
  labels:
    app: payment-processor-v2
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payment-processor-v2
  template:
    metadata:
      labels:
        app: payment-processor-v2
    spec:
      containers:
      - name: payment-processor-v2
        image: your-registry/payment-processor-v2:latest
        ports:
        - containerPort: 8000
        # Configure resource requests and limits appropriately
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        # Liveness probe ensures the application is running
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        # Readiness probe ensures the application is ready to accept traffic
        # This will fail when the application sets its 'shutting_down' flag
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
      # Crucial for graceful shutdown:
      # Gives the pod up to 60 seconds to execute its signal handler,
      # drain connections, and exit after SIGTERM is sent.
      terminationGracePeriodSeconds: 60
```

By failing the readiness probe when `shutting_down` is set, Kubernetes' `kube-proxy` will remove the pod's IP from the service endpoint, stopping new requests from reaching it. This works in conjunction with the `503` rejection in `process_payment` and Gunicorn's `graceful-timeout`.

With these changes, our `payment-processor-v2` service now gracefully handles `SIGTERM`. During deployments, pods cleanly stop accepting new traffic, complete in-flight transactions, and then exit, significantly reducing `5xx` errors and eliminating data inconsistency issues caused by abrupt terminations. While AI is a powerful tool for accelerating development, this incident reinforced that critical operational aspects of distributed systems still demand experienced engineering oversight.
