---
layout: post
title: "Fixing Performance Bottlenecks in AI-Assisted Code Reviews Due to Excessive API Call Volume"
date: 2026-04-13 10:47:21 +0000
categories: [AI, Performance]
tags: [ai, code-review, performance, kubernetes, api-performance, rate-limiting]
---

Our team recently integrated an AI-powered code review tool into our CI/CD pipeline. The idea was simple: use AI to automatically identify potential bugs, security vulnerabilities, and style inconsistencies before code reaches production. The tool, leveraging a third-party API (let's call it `CodeAnalyzerAPI`), scans each pull request, providing suggestions directly within our GitLab interface. Initially, the results were promising, catching several issues our human reviewers missed. However, as adoption increased, we started observing significant performance degradation during peak hours. Builds were taking much longer, and our API bill from `CodeAnalyzerAPI` skyrocketed.

The initial hypothesis was network saturation, but after examining network metrics on our Kubernetes cluster, that proved to be a red herring. Further investigation, using `kubectl top pod` and `kubectl describe pod <code-review-pod>`, revealed the code review pods were CPU-bound. Flamegraphs generated using `py-spy` inside the container pointed to a large amount of time spent making calls to `CodeAnalyzerAPI`.

The AI was *too* thorough. It was analyzing every single line of code in every file, resulting in thousands of individual API requests per pull request. This brute-force approach, while effective at finding issues, was clearly unsustainable.

The first step was to understand the API usage pattern. We deployed a simple sidecar container using `nicolaka/netshoot` alongside the code review pod and used `tcpdump` to capture the API traffic.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-review-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: code-review
  template:
    metadata:
      labels:
        app: code-review
    spec:
      containers:
      - name: code-review
        image: our-code-review-image:latest
        resources:
          requests:
            cpu: 1
            memory: 2Gi
          limits:
            cpu: 2
            memory: 4Gi
      - name: netshoot
        image: nicolaka/netshoot:latest
        securityContext:
          privileged: true # Necessary for tcpdump
        command: ["/bin/sleep", "infinity"]
```

After capturing the traffic for a representative pull request, we analyzed the `tcpdump` output using `tshark`:

```bash
tcpdump -i any -w capture.pcap host codeanalyzerapi.com
tshark -r capture.pcap -T fields -e http.request.method -e http.request.uri | sort | uniq -c | sort -nr
```

This confirmed our suspicion: a massive number of requests were being made for each pull request, primarily `POST` requests with code snippets.

To address this, we implemented several optimizations:

1. **Code Chunking**: Instead of sending each line of code individually, we aggregated lines into larger chunks before sending them to `CodeAnalyzerAPI`. This reduced the number of API calls significantly.

```python
def analyze_code(code_lines, api_client):
    chunk_size = 50  # Analyze 50 lines at a time
    for i in range(0, len(code_lines), chunk_size):
        chunk = code_lines[i:i + chunk_size]
        api_client.analyze("\n".join(chunk)) # Send the chunk as a single string
```

2. **Selective Analysis**: We configured the AI to skip analysis of automatically generated code, third-party libraries, and files exceeding a certain size (e.g., 2000 lines). This required integrating with our project's `.gitignore` and adding size checks:

```python
import os

def should_analyze_file(filepath, max_file_size_kb=200):
    if ".generated" in filepath or "vendor/" in filepath: #added vendor folder to prevent analyzing of third-party libraries
        return False

    file_size_kb = os.path.getsize(filepath) / 1024
    return file_size_kb <= max_file_size_kb
```

3. **Caching**: We implemented a Redis cache to store the results of previous API calls. If the same code chunk was encountered again, we retrieved the analysis from the cache instead of making a new API request. This required adding a dependency to our `requirements.txt`:

```
redis==4.6.0
```

and modifying our code to use Redis:

```python
import redis
import hashlib
import json

redis_client = redis.Redis(host='redis-service', port=6379, db=0) #Replace redis-service with actual redis hostname

def analyze_code_with_cache(code_chunk, api_client):
    cache_key = hashlib.sha256(code_chunk.encode('utf-8')).hexdigest()
    cached_result = redis_client.get(cache_key)

    if cached_result:
        return json.loads(cached_result)
    else:
        result = api_client.analyze(code_chunk)
        redis_client.set(cache_key, json.dumps(result), ex=3600) # Cache for 1 hour
        return result
```

4. **Rate Limiting**: Finally, we implemented rate limiting on the client side to prevent overwhelming `CodeAnalyzerAPI`.  We used the `tenacity` library to handle retries with exponential backoff.  This required adding the library:

```
tenacity==8.3.0
```

And then using it:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def analyze_code_with_retry(code_chunk, api_client):
    try:
        return api_client.analyze(code_chunk)
    except Exception as e:
        print(f"API call failed: {e}")
        raise

```

We also adjusted our Kubernetes resource requests and limits for the code-review pods, increasing both CPU and memory.  We deployed the new code review service using a rolling update. After deploying these changes, we observed a dramatic improvement in performance. Build times decreased significantly, and our API usage dropped by over 70%. Monitoring dashboards, built using Prometheus and Grafana, now showed stable CPU utilization for the code review pods. The errors we saw previously disappeared from the logs:

```
2026-04-09T14:30:00Z CodeAnalyzerAPI: 429 Too Many Requests
```

This incident highlights the importance of understanding the performance characteristics of third-party APIs and optimizing our code accordingly, even when using AI-powered tools. Blindly integrating these tools without considering the potential impact on system resources can lead to significant performance bottlenecks and increased costs. The combination of code chunking, selective analysis, caching, and rate limiting proved to be crucial in mitigating the performance issues and ensuring the continued scalability of our CI/CD pipeline.
