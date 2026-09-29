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

## Staying current

Engineers read this blog to learn how to do things *now*, so every article is written
against the current release of what it covers, not the version most tutorials assume.

- **Name the versions.** State the versions the article and its code target (for
  example "PostgreSQL 18, PgBouncer 1.26") near the top, and pin them in the code.
- **Read the recent release notes before writing.** At least the last two major or
  minor releases of each main technology, plus its deprecation notices. If the
  recommended approach changed, teach the new one and say what it replaced.
- **Say what is not ready.** Beta, alpha and preview features can be mentioned, but
  labelled as such and never used as the default recommendation. Name a release that
  is imminent (a beta or release candidate) if it changes the advice.
- **Security first.** If the latest release of a covered tool fixes a vulnerability,
  tell readers which version to run.
- **Keep it current.** When a covered release changes the advice, update the article
  and its `updated:` date rather than letting it drift.

## Backlog

Ordered by how much the topic has changed recently and how time-sensitive it is.
Current state verified against official sources on 2026-09-29; re-check the release
notes before writing, since these move. The article must still cite what it actually
uses.

| # | Topic and 2026 angle | Category · kind | What changed (verified 2026-09-29) | Links to | Start from |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Kafka consumer rebalances with the new protocol.** What happens to in-flight records when the broker assigns partitions incrementally | Distributed Systems · Deep Dive | Kafka 4.3.1 current. KIP-848 protocol GA since 4.0 but opt-in (`group.protocol=consumer`); planned default in 5.0. Share groups (KIP-932, "Queues for Kafka") production-ready in 4.2 | idempotent Kafka consumers, transactional outbox, retries | [Consumer rebalance protocol](https://kafka.apache.org/43/operations/consumer-rebalance-protocol/), [Kafka upgrade notes](https://kafka.apache.org/43/getting-started/upgrade/) |
| 2 | **PgBouncer transaction mode in 2026.** Prepared statements work now; what still needs session mode | Database · Guide | PgBouncer 1.26.0 (2026-09-23) fixes CVE-2026-19888 (SCRAM login crash); tracks `search_path` on PostgreSQL 18+. Protocol-level prepared statements in transaction mode since 1.21 (`max_prepared_statements`) | transactional outbox, resource requests and limits | [PgBouncer changelog](https://www.pgbouncer.org/changelog.html), [PgBouncer configuration](https://www.pgbouncer.org/config.html) |
| 3 | **Verifying signed images at admission.** cosign v3 keyless signing, verified by Kyverno's CEL policies or policy-controller | Security · Guide | cosign 3.1.3: bundle format on by default. Kyverno `ClusterPolicy`/`Policy` (and `verifyImages`) deprecated in 1.19, removed in 1.20: use `ImageValidatingPolicy`. Rekor v2 GA, but the public instance still defaults to Rekor v1 | OPA Gatekeeper, multi-stage builds, security best practices | [cosign changelog](https://github.com/sigstore/cosign/blob/main/CHANGELOG.md), [Kyverno policy types](https://kyverno.io/docs/policy-types/cluster-policy/overview/), [policy-controller](https://docs.sigstore.dev/policy-controller/overview/) |
| 4 | **Surviving node drains.** PodDisruptionBudgets, native sidecars and the new node drain conditions | Kubernetes · Guide | Kubernetes 1.37 current. `unhealthyPodEvictionPolicy` stable since 1.31 (default `IfHealthyBudget`; prefer `AlwaysAllow`). Native sidecars stable since 1.33. 1.37 adds `DrainInProgress`/`Drained` node conditions (check maturity) | cluster upgrades, graceful shutdown, topology spread | [Configure a PDB](https://kubernetes.io/docs/tasks/run-application/configure-pdb/), [Sidecar containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/), [Kubernetes 1.37 release](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) |
| 5 | **PostgreSQL 18 indexes.** When skip scan replaces an index, and when partial and covering indexes still win | Database · Deep Dive | PostgreSQL 18.6 current; 19 in beta. PG 18 adds B-tree skip scan (multicolumn indexes without a leading `=` condition); PG 17 improved `IN` lookups | transactional outbox | [PostgreSQL 18 release](https://www.postgresql.org/about/news/postgresql-18-released-3142/), [PG 18 release notes](https://www.postgresql.org/docs/18/release-18.html), [Partial indexes](https://www.postgresql.org/docs/current/indexes-partial.html) |
| 6 | **Zero-downtime schema changes on PostgreSQL 18.** Expand and contract with the new constraint options | Database · Guide | PG 18: `NOT NULL` constraints can be added `NOT VALID` and validated later; `CHECK`/foreign keys can be `NOT ENFORCED`; virtual generated columns are the default. PG 19 (beta) adds `REPACK` without an exclusive lock: mention, do not recommend | Flyway migrations, blue-green deployments | [PG 18 release notes](https://www.postgresql.org/docs/18/release-18.html), [Martin Fowler: Parallel Change](https://martinfowler.com/bliki/ParallelChange.html) |
| 7 | **Autoscaling on queue depth: KEDA or the HPA?** | Platform Engineering · Guide | KEDA 2.21.0 (2026-09-23) fixes CVE-2026-77524; per-trigger fallback with `scalingModifiers`. Kubernetes 1.37: HPA scale-to-zero is beta and on by default | requests and limits, SQS message groups, retries | [KEDA releases](https://github.com/kedacore/keda/releases), [KEDA SQS scaler](https://keda.sh/docs/2.21/scalers/aws-sqs/), [Kubernetes 1.37 release](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) |
| 8 | **Tracing a Python service with OpenTelemetry.** Zero-code first, then manual spans, on the stable conventions | Reliability · Guide | opentelemetry-python 1.45.0 (2026-09-25): traces and metrics stable, logs in development. HTTP and (for PostgreSQL/MySQL) database semantic conventions stable; opt in with `OTEL_SEMCONV_STABILITY_OPT_IN`. Profiles signal alpha, no Python SDK | Prometheus and Grafana, graceful shutdown | [OTel Python](https://opentelemetry.io/docs/languages/python/), [Zero-code Python](https://opentelemetry.io/docs/zero-code/python/), [HTTP span conventions](https://opentelemetry.io/docs/specs/semconv/http/http-spans/) |
| 9 | **Backpressure and load shedding in asyncio on Python 3.14/3.15** | Performance · Guide | Python 3.14.7 current; 3.15.0 due 2026-10-01 (adds `TaskGroup.cancel`). 3.14: free-threading officially supported, `python -m asyncio ps`/`pstree`. `Queue.shutdown` since 3.13 | asyncio basics, advanced asyncio, rate limiting, retries | [What's new in 3.14](https://docs.python.org/3/whatsnew/3.14.html), [What's new in 3.15](https://docs.python.org/3.15/whatsnew/3.15.html), [asyncio queues](https://docs.python.org/3/library/asyncio-queue.html), [SRE Book: Handling overload](https://sre.google/sre-book/handling-overload/) |
| 10 | **NetworkPolicies from default-deny to least privilege** | Security · Guide | `networking.k8s.io/v1` NetworkPolicy unchanged. AdminNetworkPolicy/BaselineAdminNetworkPolicy merged into `ClusterNetworkPolicy` (network-policy-api v0.2.0, `v1alpha2`, alpha; limited CNI support): sidebar only | Kubernetes networking, security best practices | [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/), [network-policy-api v0.2.0](https://github.com/kubernetes-sigs/network-policy-api/releases/tag/v0.2.0), [Implementations](https://network-policy-api.sigs.k8s.io/implementations/) |
| 11 | **SLOs and error budgets for one service** | Reliability · Guide | Multiwindow, multi-burn-rate alerts (14.4 / 6 / 1 for a 99.9% SLO) remain the reference; OpenSLO lists v1 and v2alpha schemas | Prometheus and Grafana, canary deployments | [SRE Workbook: Implementing SLOs](https://sre.google/workbook/implementing-slos/), [SRE Workbook: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/), [OpenSLO](https://openslo.com/) |
| 12 | **Cache stampedes, stale reads and TTL jitter** | Performance · Guide | Redis 8.10 (AGPLv3 available again since Redis 8) and Valkey 9.1 (BSD fork). Per-field expiry (`HEXPIRE`, since 7.4); client-side caching with its documented stale-read race | Redis caching, rate limiting | [Client-side caching](https://redis.io/docs/latest/develop/reference/client-side-caching/), [HEXPIRE](https://redis.io/docs/latest/commands/hexpire/), [AWS caching best practices](https://aws.amazon.com/caching/best-practices/) |
| 13 | **Argo Rollouts vs Flagger** | DevOps · Comparison | Argo Rollouts 1.10.0: Gateway API through a plugin (plugin system alpha). Flagger 1.45.0: Gateway API built in | both canary articles, blue-green deployments | [Argo Rollouts plugins](https://argoproj.github.io/argo-rollouts/features/traffic-management/plugins/), [Flagger Gateway API](https://docs.flagger.app/tutorials/gatewayapi-progressive-delivery) |

Published from this list: Retries with exponential backoff and jitter (2026-09-29).
When a topic is published, move it to that line. When fewer than five topics remain,
propose new ones from the target mix above, each with a 2026 angle and verified sources.

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
