# Editorial guide

What to write next for [blog.riteshrana.engineer](https://blog.riteshrana.engineer),
and how. For people and for the Muse content agent. The mechanics of adding an
article (folders, front matter, validation) are in
[content-authoring.md](content-authoring.md); this guide is about choosing and
shaping the article itself.

## Where the blog is today (September 2026)

- 58 published articles. Kubernetes (14) and AI (11) dominate; Database, Security
  and Performance have one article each, Reliability three.
- 11 of the 20 most recent articles follow one formula, "Fixing X in AI-generated Y
  on Kubernetes", and all 11 are invented incident narratives now labelled
  `scenario: illustrative`.
- Titles lean on templates: 7 start with "Boosting", 7 with "Fixing", 3 with
  "Leveraging".
- The strongest recent article, the transactional outbox guide, is a well-sourced
  explanation of one idea, with code that matches its text and a diagram.

The goal is more articles like that one: fewer formulaic incident stories, more
sourced guides that fill the gaps.

## Target mix for the next 10 articles

| Share | Kind | Examples |
| :--- | :--- | :--- |
| 4 | **Guide** on a core concept, sourced from official docs or papers | Retries with jitter, PgBouncer pooling modes, NetworkPolicies |
| 2 | **Deep Dive** into how something works | Kafka rebalances, index-only scans |
| 1 | **Comparison** with a clear recommendation | Argo Rollouts vs Flagger |
| 1 | **Case Study** of a real, citable event (public postmortem, your own measured work) | Only with sources; otherwise don't |
| 1 | **Scenario** (`scenario: illustrative`), at most one in ten | A made-up incident that teaches a technique |
| 1 | **AI engineering** that is not "fixing AI-generated code" | Evaluating LLM features, guardrails, cost control |

Across any 10 consecutive articles: at least 2 Database, Security or Performance
articles, and no more than 3 on Kubernetes.

## What makes an article worth publishing

1. **One idea, fully explained.** The reader finishes knowing when to use it, how it
   fails, and what to do instead.
2. **Checkable.** Every factual claim a reader could verify links to the primary
   source (official docs, RFCs, papers, public postmortems). At least 3 references.
3. **Correct code.** Code runs as shown and matches the prose. No placeholder
   variables in prose, no `[TODO]`.
4. **Figures** that show the system's state and how it changes: about one per
   400-600 words of explanation, hand-drawn SVG per [figures.md](figures.md), animated
   when order matters. A fenced `mermaid` block is fine for a simple flowchart or
   sequence where layout carries no meaning.
5. **Connected.** 2–4 links to related articles on the blog, on phrases already in
   the text.
6. **Honest.** No invented incidents presented as real, no invented numbers, no
   real product blamed for an invented failure. See *Accuracy* in
   [content-authoring.md](content-authoring.md#accuracy).

## Titles

Say what the article is about, plainly:

| Avoid | Prefer |
| :--- | :--- |
| Boosting API Performance with gRPC-Web: A Practical Guide | gRPC-Web: Calling gRPC Services from the Browser |
| Leveraging AWS SQS Message Groups for Ordered Processing | Ordered Processing with SQS FIFO Message Groups |
| Fixing Idempotency Gaps in AI-Generated Kafka Consumers on Kubernetes | Idempotent Kafka Consumers: Deduplicating Redelivered Messages |

Avoid the openers *Boosting*, *Leveraging*, *Unlocking*, *Mastering*, and the
"… in AI-generated … on Kubernetes" pattern; the content validator warns about
them. Aim for under 70 characters.

## Backlog

Topics that fill gaps and connect to existing articles. Each lists primary sources
to start from (all verified reachable in September 2026); the article must still
cite what it actually uses.

| Topic | Category · kind | Links to | Start from |
| :--- | :--- | :--- | :--- |
| Retries with exponential backoff and jitter | Distributed Systems · Guide | idempotent operations, circuit breaker | [AWS Builders' Library: Timeouts, retries and backoff with jitter](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter), [AWS Architecture Blog: Exponential backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), [SRE Book: Addressing cascading failures](https://sre.google/sre-book/addressing-cascading-failures/), [AWS SDKs: Retry behavior](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html) |
| PostgreSQL connection pooling with PgBouncer: session vs transaction mode | Database · Guide | transactional outbox, resource requests and limits | [PgBouncer features](https://www.pgbouncer.org/features.html), [PostgreSQL connection settings](https://www.postgresql.org/docs/current/runtime-config-connection.html) |
| Partial and covering indexes in PostgreSQL | Database · Deep Dive | transactional outbox | [Partial indexes](https://www.postgresql.org/docs/current/indexes-partial.html), [Index-only scans](https://www.postgresql.org/docs/current/indexes-index-only-scans.html) |
| Zero-downtime schema changes with expand and contract | Database · Guide | Flyway migrations, blue-green deployments | [Martin Fowler: Parallel Change](https://martinfowler.com/bliki/ParallelChange.html) |
| Kafka consumer rebalances: what happens to in-flight messages | Distributed Systems · Deep Dive | idempotent Kafka consumers, transactional outbox | [Kafka documentation](https://kafka.apache.org/documentation/), [KIP-429 incremental rebalancing](https://cwiki.apache.org/confluence/display/KAFKA/KIP-429%3A+Kafka+Consumer+Incremental+Rebalance+Protocol) |
| PodDisruptionBudgets: surviving node drains | Kubernetes · Guide | cluster upgrades, graceful shutdown, topology spread | [Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/), [Configure a PDB](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) |
| Autoscaling on queue depth with KEDA | Platform Engineering · Guide | requests and limits, SQS message groups | [KEDA concepts](https://keda.sh/docs/latest/concepts/) |
| NetworkPolicies from default-deny to least privilege | Security · Guide | Kubernetes networking, security best practices | [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| Signing container images with Sigstore cosign | Security · Guide | multi-stage builds, OPA Gatekeeper | [cosign signing overview](https://docs.sigstore.dev/cosign/signing/overview/) |
| SLOs and error budgets for one service | Reliability · Guide | Prometheus and Grafana, canary deployments | [SRE Workbook: Implementing SLOs](https://sre.google/workbook/implementing-slos/) |
| Load shedding and backpressure in asyncio services | Performance · Guide | asyncio basics, advanced asyncio, rate limiting | [asyncio queues](https://docs.python.org/3/library/asyncio-queue.html), [SRE Book: Handling overload](https://sre.google/sre-book/handling-overload/) |
| Cache stampedes, stale reads and TTL jitter | Performance · Guide | Redis caching | [AWS caching best practices](https://aws.amazon.com/caching/best-practices/) |
| Tracing a Python service with OpenTelemetry | Reliability · Guide | Prometheus and Grafana, graceful shutdown | [OpenTelemetry for Python](https://opentelemetry.io/docs/languages/python/) |
| Argo Rollouts vs Flagger | DevOps · Comparison | both canary articles, blue-green deployments | [Argo Rollouts](https://argoproj.github.io/argo-rollouts/), [Flagger](https://docs.flagger.app/) |

When a backlog topic is published, remove it from this table.

## Brief for Muse

The full, detailed prompt (research, structure, code standards, adversarial review,
output) is [article-generation-prompt.md](article-generation-prompt.md). Use it for
every article; the short version below is a summary.

> Write one article from the backlog in `docs/editorial-guide.md` (or propose a
> topic that fills a gap listed there). Follow `docs/content-authoring.md` exactly.
> Explain one idea completely: when to use it, how it works, how it fails, what to
> do instead. Cite at least 3 primary sources you actually opened, as
> `[Title](url)` links under `## References`. Draw SVG figures per
> `docs/figures.md` wherever the idea is a flow, a state change or a data layout,
> and link 2–4 related articles on this blog. Code
> must run as shown and match the prose. Use a plain, specific title without the
> openers Boosting, Leveraging, Unlocking or Mastering. Do not invent incidents,
> measurements or quotes; if you narrate a made-up situation, set
> `scenario: illustrative`. Run `ruby scripts/validate_content.rb` and
> `ruby scripts/check_external_links.rb content/posts/<slug>` before opening the
> pull request.
