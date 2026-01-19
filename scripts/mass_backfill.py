import os
import time
import random
import re
from datetime import datetime, timedelta
from pathlib import Path
from google import genai
from google.genai import types

# Categories to ensure diversity
CATEGORIES = {
    "Kubernetes": [
        "Advanced Kubectl Tips for Power Users",
        "Understanding Kubernetes Networking Deep Dive",
        "Kubernetes Security Best Practices 2026",
        "Setting up a K8s Cluster on Bare Metal",
        "Troubleshooting CrashLoopBackOff Errors",
        "Helm vs Kustomize: A Comprehensive Comparison",
        "Managing StatefulSets in Production",
        "Kubernetes Cost Optimization Strategies",
        "Service Mesh with Istio: A Practical Guide",
        "GitOps with ArgoCD and Kubernetes",
        "Kubernetes Operators 101: Writing Your Own",
        "Pod Topology Spread Constraints Explained",
        "Securing Secrets in Kubernetes with Vault",
        "Monitoring K8s with Prometheus and Grafana",
        "Blue-Green Deployments on Kubernetes",
        "Canary Deployments with Flagger",
        "Autoscaling: HPA and VPA Explained",
        "Debug Container Networking with Ephemeral Containers",
        "Kubernetes Resource Requests and Limits Masterclass",
        "Upgrading Kubernetes Clusters with Zero Downtime"
    ],
    "Python": [
        "Python 3.14 Features You Should Know",
        "Advanced AsyncIO Patterns in Python",
        "Python Type Hinting: Beyond the Basics",
        "Optimizing Python Performance with Profiling",
        "Building a Custom Linter with AST",
        "Python Metaclasses: What, Why, and How",
        "Data Classes vs Pydantic Models",
        "Building High-Performance APIs with FastAPI",
        "Python Concurrency: Eeads vs Processes vs Async",
        "Memory Management in Python: GC Deep Dive",
        "Design Patterns in Python: The Singleton",
        "Design Patterns in Python: The Factory",
        "Design Patterns in Python: The Observer",
        "Design Patterns in Python: The Decorator",
        "Mastering Python Generators and Iterators",
        "Context Managers in Python: Writing Your Own",
        "Python Decorators: A Comprehensive Guide",
        "Testing in Python: Pytest Best Practices",
        "Mocking External Services in Python Tests",
        "Packaging and Publishing Python Libraries"
    ],
    "DevOps": [
        "Terraform Best Practices for Large Scale Infra",
        "Ansible for Configuration Management in 2026",
        "Jenkins vs GitHub Actions: The Ultimate Showdown",
        "Building a Secure CI/CD Pipeline",
        "Infrastructure as Code: Security Scanning with Checkov",
        "Zero Trust Security for DevOps Pipelines",
        "Managing Multi-Cloud Infrastructure",
        "Cost Management in AWS/Azure/GCP",
        "Log Aggregation Strategies (ELK vs Loki)",
        "Distributed Tracing with Jaeger",
        "Chaos Engineering: Breaking Things on Purpose",
        "SRE Principles for DevOps Teams",
        "Incident Management and Post-Mortems",
        "Docker Security Scanning in CI/CD",
        "Managing Secrets in CI/CD Pipelines",
        "Ephemeral Environments for Pull Requests",
        "DevSecOps: Shifting Security Left",
        "Performance Testing in CI/CD with K6",
        "Documentation as Code with MkDocs",
        "Automating Database Migrations in Pipelines"
    ],
    "System Design": [
        "Designing a URL Shortener (System Design Interview)",
        "Designing specific Rate Limiter Algorithms",
        "Consistent Hashing Explained Simply",
        "CAP Theorem in Practice",
        "Database Sharding Strategies",
        "Caching Strategies: Write-Through vs Write-Back",
        "Message Queues: Kafka vs RabbitMQ",
        "Designing for High Availability",
        "Load Balancing Algorithms Explained",
        "Database Replication Modes",
        "NoSQL vs SQL: When to Choose What",
        "Designing a Chat Application Architecture",
        "Designing a Notification System",
        "Bloom Filters: Probabilistic Data Structures",
        "Distributed Consensus: Raft vs Paxos",
        "Leader Election in Distributed Systems",
        "Idempotency in API Design",
        "API Gateway Pattern Explained",
        "Microservices vs Monolith: The Decision Framework",
        "Saga Pattern for Distributed Transactions"
    ],
    "Cloud & AWS": [
        "AWS Lambda Cold Starts: How to Mitigate",
        "DynamoDB Single Table Design Patterns",
        "AWS ECS Fargate vs standard EC2",
        "S3 Storage Classes and Lifecycle Rules",
        "Route53 Traffic Flow policies",
        "AWS IAM Best Practices for Least Privilege",
        "Serverless Methodologies on AWS",
        "CloudFormation vs Terraform on AWS",
        "Optimizing AWS Costs with Savings Plans",
        "Building Event-Driven Architectures with EventBridge",
        "AWS Step Functions for State Machine Orchestration",
        "CDN Strategies with CloudFront",
        "VPC Networking Fundamentals",
        "AWS RDS Proxy for Connection Pooling",
        "Aurora Global Database Architecture",
        "Securing S3 Buckets: A Checklist",
        "AWS X-Ray for Distributed Debugging",
        "Deploying Static Sites to S3 + CloudFront",
        "AWS Glue for ETL Pipelines",
        "Cognito for User Authentication"
    ]
}

# Expand categories to fill 280 (simple expansion for the sake of the script logic)
# Ideally we would list all 280, but for this script we will combine subjects + angles
ANGLES = [
    "A Beginner's Guide", "Deep Dive", "Best Practices", "Common Pitfalls", 
    "In Production", "Performance Tuning", "Security Guide", "Interview Guide"
]

def generate_topics(target_count=280):
    topics = []
    
    # 1. Add specific hand-curated topics first (100)
    for category, titles in CATEGORIES.items():
        topics.extend(titles)
        
    # 2. Generate combinations for the rest
    subjects = [
        "PostgreSQL", "Redis", "MongoDB", "Cassandra", "Elasticsearch", "Neo4j",
        "Nginx", "Traefik", "Envoy", "HAProxy",
        "Linux Kernel", "Bash Scripting", "Systemd", "eBPF",
        "React", "Vue.js", "Angular", "Svelte", "Next.js",
        "Go", "Rust", "Java", "C++", "TypeScript",
        "GraphQL", "gRPC", "WebSockets", "REST",
        "OAuth2", "JWT", "OpenID Connect", "mTLS",
        "Prometheus", "Grafana", "Datadog", "New Relic"
    ]
    
    random.shuffle(subjects)
    
    while len(topics) < target_count:
        for subject in subjects:
            for angle in ANGLES:
                topic = f"{subject}: {angle}"
                if topic not in topics:
                    topics.append(topic)
                    if len(topics) >= target_count:
                        break
            if len(topics) >= target_count:
                break
                
    return topics[:target_count]

def get_backfill_prompt(title, author="ritesh"):
    return f"""You are a Staff Software Engineer and Technical Writer. Generate ONE original technical blog post.
    
TOPIC: {title}
AUTHOR: {author}

CRITICAL INSTRUCTIONS:
1. **NO HALLUCINATIONS**: Do not invent libraries/commands.
2. **STRICT FORMAT**: Use the specific Jekyll front matter below.
3. **QUALITY**: 800-1200 words, practical code examples, SEO optimized.

Structure:
---
layout: post
title: "{title}"
date: {{DATE}}
categories: [Tech, Engineering]
tags: [tech, software, engineering]
author: {author}
---

## Introduction...
## Core Concepts...
## Implementation...
...
## Conclusion...

Generate the content now.
"""

def save_post(content, date_obj):
    # Fix front matter date
    date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S +0000")
    content = content.replace("{{DATE}}", date_str)
    
    # Extract Title for filename
    title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if not title_match:
        print("Error: No title found")
        return None
        
    title = title_match.group(1)
    slug = re.sub(r'[^\w\s-]', '', title.lower()).replace(' ', '-').strip('-')
    
    filename = f"{date_obj.strftime('%Y-%m-%d')}-{slug}.md"
    path = Path(f"_posts/{filename}")
    
    with open(path, "w") as f:
        f.write(content)
        
    return path

def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("No API KEY")
        return

    client = genai.Client(api_key=api_key)
    topics = generate_topics(280)
    print(f"Goal: {len(topics)} posts.")
    
    # Backdate starting from 1 year ago
    start_date = datetime.now() - timedelta(days=365)
    
    for i, topic in enumerate(topics):
        # Distribute dates linearly over the year
        post_date = start_date + timedelta(days=i * (365/280))
        
        print(f"[{i+1}/{len(topics)}] Generating: {topic}")
        
        prompt = get_backfill_prompt(topic)
        
        try:
            # Using the exact model and config settings/structure as the original script
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            if response and response.text:
                # Basic cleanup
                clean_text = response.text.replace('```markdown', '').replace('```', '').strip()
                if "layout: post" not in clean_text:
                    clean_text = "---\nlayout: post\n" + clean_text
                
                path = save_post(clean_text, post_date)
                print(f"  Saved to {path}")
            
            # Rate limit handling (avoid hitting quota with 280 requests)
            time.sleep(2) 
            
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
