---
layout: page
icon: fas fa-gift
order: 9
title: Free Dev Stuff
permalink: /free-stuff/
---

## 🎁 Opinionated Free Tier Stack

As engineers, we don't need a directory of 400 "maybe free" services. We need the tools that actually work for prototypes, homelabs, and MVPs without surprise billing. 

Here is my highly curated, strictly opinionated list of the best developer-first free tiers and self-hostable tools available right now.

---

### <i class="fas fa-server text-primary"></i> Compute & Hosting

- **Fly.io**
  - **Best For:** Containerized App Servers and Edge Compute
  - **The Free Tier:** Up to 3 shared-cpu-1x VMs (2,340 hours/mo). Perfect for deploying Docker containers via CLI globally.
- **Vercel**
  - **Best For:** Serverless Next.js, React Frontends, and Edge Functions
  - **The Free Tier:** Unlimited deployments, 100GB bandwidth. The easiest way to ship a frontend.
- **Cloudflare Workers**
  - **Best For:** Edge Compute and Serverless APIs
  - **The Free Tier:** 100k requests/day. Excellent for fast, globally distributed stateless execution.

### <i class="fas fa-database text-success"></i> Databases & State

- **Supabase**
  - **Best For:** All-in-one Postgres Backend & Authentication
  - **The Free Tier:** 500MB database, 1GB storage, 50k MAU Auth. The ultimate open-source Firebase alternative.
- **Neon**
  - **Best For:** Serverless Postgres
  - **The Free Tier:** 1 project, 3GiB storage, branching out of the box. Great developer experience for SQL.
- **Upstash**
  - **Best For:** Serverless Redis and Kafka
  - **The Free Tier:** 10k commands per day. Unmatched for rate limiting, caching, and simple pub/sub in serverless apps.

### <i class="fas fa-key text-warning"></i> Authentication

- **Clerk**
  - **Best For:** Drop-in Next.js/React Authentication
  - **The Free Tier:** 10,000 Monthly Active Users. Ridiculously fast integration and polished UI components.
- **Logto**
  - **Best For:** Custom Identity Infrastructure
  - **The Free Tier:** 50,000 MAU on cloud. Open-source friendly with great developer documentation.

### <i class="fas fa-sync text-danger"></i> CI/CD & Deploy Orchestration

- **GitHub Actions**
  - **Best For:** Universal CI/CD Pipelines
  - **The Free Tier:** 2,000 orchestration minutes/month. The industry standard limit.
- **Earthly**
  - **Best For:** Containerized Build Automation
  - **The Free Tier:** 6,000 build minutes/month. Excellent for ensuring builds run exactly the same locally as in CI.

### <i class="fas fa-chart-line text-secondary"></i> Observability

- **Sentry**
  - **Best For:** Error Tracking & Stack Trace Capturing
  - **The Free Tier:** 5K errors/month. Crucial for catching unhandled exceptions in production MVPs.
- **Grafana Cloud**
  - **Best For:** Metrics, Logs, and Dashboards
  - **The Free Tier:** 10k Prometheus metrics, 50GB logs, 50GB traces. A generous starting point for the LGTM stack.

---

### 📝 Notice a discrepancy?

Is a free tier dead? Did a company pull a bait-and-switch? [Open an issue](https://github.com/ambicuity/Tech-Blog/issues/new) to have it removed from this opinionated index.
