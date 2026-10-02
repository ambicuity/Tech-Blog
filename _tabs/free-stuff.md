---
layout: page
icon: fas fa-gift
order: 9
title: Free Developer Tools & Services
permalink: /free-stuff/
wide: true
eyebrow: Resources
lede: A curated list of genuinely useful free tiers, open-source alternatives and free trials for engineers — opinionated, verified, and labelled so you know what you’re actually signing up for.
last_verified: 2026-09-25
---
{%- assign _items = site.data.resources.items -%}
{%- assign _groups = site.data.resources.groups -%}
{%- assign _removed = site.data.resources.removed | default: empty -%}

## The shortlist

Free tiers change without notice. Every entry below is labelled so you can tell at a glance whether it's a **free forever**, **free tier**, **free trial**, or **open-source** offering — and whether it needs a credit card to sign up.

<aside class="callout callout--warning resource-disclaimer" aria-label="Warning">
  <p class="callout__label">Check before you build</p>
  <p>Free tiers change without notice. Every entry shows when its details were last re-checked — confirm limits on the official pricing page before depending on them. Last bulk re-check: <time datetime="2026-09-25">September 25, 2026</time>.</p>
</aside>

<div class="resource-toolbar" hidden data-resource-controls>
  <label class="visually-hidden" for="resource-filter">Filter resources</label>
  <input class="input input--sm" id="resource-filter" type="search" placeholder="Filter by name or use case…" autocomplete="off" data-resource-filter>
  <div class="resource-pillset" role="group" aria-label="Filter by tier">
    <span class="visually-hidden">Tier</span>
    <span class="pill"><input type="checkbox" id="filter-free-forever" data-tier-filter="free_forever"><label for="filter-free-forever">Free forever</label></span>
    <span class="pill"><input type="checkbox" id="filter-free-tier" data-tier-filter="free_tier"><label for="filter-free-tier">Free tier</label></span>
    <span class="pill"><input type="checkbox" id="filter-open-source" data-tier-filter="open_source"><label for="filter-open-source">Open source</label></span>
    <span class="pill"><input type="checkbox" id="filter-free-trial" data-tier-filter="free_trial"><label for="filter-free-trial">Free trial</label></span>
  </div>
  <div class="resource-pillset" role="group" aria-label="Filter by requirements">
    <span class="visually-hidden">Requirements</span>
    <span class="pill"><input type="checkbox" id="filter-no-card" data-card-filter="no"><label for="filter-no-card">No credit card</label></span>
    <span class="pill"><input type="checkbox" id="filter-commercial-ok" data-commercial-filter="yes"><label for="filter-commercial-ok">Commercial OK</label></span>
    <span class="pill"><input type="checkbox" id="filter-self-host" data-selfhost-filter="yes"><label for="filter-self-host">Self-hostable</label></span>
  </div>
  <p class="visually-hidden" role="status" aria-live="polite" data-resource-status></p>
</div>

## Top picks (2026)

If you only bookmark a handful, start with the eight below. They cover a complete personal SaaS at $0/month within the published limits and all four are quiet about billing.

<div class="top-picks">
  <article class="top-pick">
    <h3>Cloudflare Workers</h3>
    <p>Edge API and background logic. 100k requests/day, no card needed, with a generous Workers Paid path when you outgrow it.</p>
    <p class="top-pick__meta">100k req/day · No card · Commercial OK</p>
  </article>
  <article class="top-pick">
    <h3>Vercel</h3>
    <p>Next.js / React frontends with edge functions. Hobby plan gives you 100 GB of bandwidth and zero cold-start pain.</p>
    <p class="top-pick__meta">100 GB/mo · No card · Commercial OK</p>
  </article>
  <article class="top-pick">
    <h3>Supabase</h3>
    <p>Postgres, auth, storage and realtime in one package. 500 MB DB on the free plan; open source so you can self-host out of it.</p>
    <p class="top-pick__meta">500 MB · OSS · Free · Pauses after 1 wk idle</p>
  </article>
  <article class="top-pick">
    <h3>Cloudflare R2</h3>
    <p>S3-compatible object storage with zero egress fees. 10 GB of free storage paired with Cloudflare's CDN is hard to beat.</p>
    <p class="top-pick__meta">10 GB · Card req · Commercial OK · No egress</p>
  </article>
  <article class="top-pick">
    <h3>Resend</h3>
    <p>Developer-first transactional email with React Email templates. 3,000 emails/month and 100/day on the Free plan.</p>
    <p class="top-pick__meta">3,000 emails/mo · No card · Commercial OK</p>
  </article>
  <article class="top-pick">
    <h3>GitHub Actions</h3>
    <p>CI/CD on every GitHub repo. 2,000 minutes/month for private repos and unlimited minutes for public ones.</p>
    <p class="top-pick__meta">2,000 min/mo · No card · Public = unlimited</p>
  </article>
  <article class="top-pick">
    <h3>Sentry</h3>
    <p>Error tracking with first-class stack captures for Python, JS, Go, Java and more. 5k errors/month is plenty for an MVP.</p>
    <p class="top-pick__meta">5k errors/mo · No card · OSS self-host</p>
  </article>
  <article class="top-pick">
    <h3>Hugging Face Inference</h3>
    <p>Hosted inference for thousands of OSS models. Free tier covers a lot of one-shot LLM, embedding and vision workloads.</p>
    <p class="top-pick__meta">Serverless · No card · OSS model zoo</p>
  </article>
</div>

## My recommended $0 stack

For a personal SaaS / MVP / homelab side-project at $0/month inside the published free limits.

<div class="recommended-stack">
  <dl>
    <dt><span class="recommended-stack__step">01</span> Frontend</dt>
    <dd><a href="https://vercel.com/" rel="noopener">Vercel</a> — Next.js / React deploys and edge functions, 100 GB bandwidth/month.</dd>
    <dt><span class="recommended-stack__step">02</span> API / edge logic</dt>
    <dd><a href="https://workers.cloudflare.com/" rel="noopener">Cloudflare Workers</a> — 100k requests/day with the workerd runtime also being open source.</dd>
    <dt><span class="recommended-stack__step">03</span> Database</dt>
    <dd><a href="https://supabase.com/" rel="noopener">Supabase</a> — Postgres with auth, storage and realtime in one package; open source so you can leave on a lean one.</dd>
    <dt><span class="recommended-stack__step">04</span> Authentication</dt>
    <dd><a href="https://logto.io/" rel="noopener">Logto</a> or <a href="https://clerk.com/" rel="noopener">Clerk</a> — 50k MAU on Logto Cloud, 10k MAU on Clerk; Logto's core is OSS.</dd>
    <dt><span class="recommended-stack__step">05</span> Object storage</dt>
    <dd><a href="https://developers.cloudflare.com/r2/" rel="noopener">Cloudflare R2</a> — S3-compatible storage with no egress fees.</dd>
    <dt><span class="recommended-stack__step">06</span> Email</dt>
    <dd><a href="https://resend.com/" rel="noopener">Resend</a> for transactional, <a href="https://www.brevo.com/" rel="noopener">Brevo</a> if you also need marketing.</dd>
    <dt><span class="recommended-stack__step">07</span> Background work</dt>
    <dd><a href="https://upstash.com/qstash" rel="noopener">Upstash QStash</a> for HTTP-based cron / queues, or <a href="https://www.inngest.com/" rel="noopener">Inngest</a> for durable function flows.</dd>
    <dt><span class="recommended-stack__step">08</span> CI/CD</dt>
    <dd><a href="https://github.com/features/actions" rel="noopener">GitHub Actions</a> — 2,000 min/month on private repos, unlimited on public.</dd>
    <dt><span class="recommended-stack__step">09</span> Error tracking</dt>
    <dd><a href="https://sentry.io/" rel="noopener">Sentry</a> — 5k errors/month and a self-hostable OSS core.</dd>
    <dt><span class="recommended-stack__step">10</span> Product analytics</dt>
    <dd><a href="https://posthog.com/" rel="noopener">PostHog</a> — 1 M events and 5k recordings/month, OSS and self-hostable.</dd>
    <dt><span class="recommended-stack__step">11</span> Privacy analytics</dt>
    <dd><a href="https://umami.is/" rel="noopener">Umami</a> — fully open source, self-host for $0.</dd>
    <dt><span class="recommended-stack__step">12</span> DNS / CDN</dt>
    <dd><a href="https://www.cloudflare.com/" rel="noopener">Cloudflare</a> free plan — DNS, CDN, DDoS protection and Turnstile CAPTCHA in one.</dd>
  </dl>
  <p class="recommended-stack__cost">Estimated monthly cost: <strong>$0</strong> within free limits.</p>
</div>

## $0 architecture

What the stack above looks like when you wire it together.

                 ┌───────────────┐
                 │    Users      │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  Cloudflare   │
                 │   DNS / WAF   │
                 └───────┬───────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        ┌───────────┐         ┌───────────┐
        │  Vercel   │         │ Workers   │
        │ Frontend  │         │   API     │
        └───────────┘         └─────┬─────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                  ┌─────────┐           ┌─────────┐
                  │Supabase │           │   R2    │
                  │ Postgres│           │ Storage │
                  └─────────┘           └─────────┘

The diagram shows a $12 split between edge (Cloudflare), frontend (Vercel), API (Cloudflare Workers), state (Supabase Postgres) and storage (Cloudflare R2).

## Build this for $0

Common stacks you can build with the entries on this page, end to end, without paying anyone.

<ul class="revenue-grid">
  <li>
    <h4>Personal SaaS / MVP</h4>
    <p>Vercel · Cloudflare Workers · Supabase · Logto · R2 · Resend · GitHub Actions · Sentry · PostHog · Cloudflare DNS.</p>
    <p class="revenue-grid__cost">~$0/month within free limits.</p>
  </li>
  <li>
    <h4>AI app / RAG prototype</h4>
    <p>Cloudflare Workers · Supabase · Groq or Gemini API · Qdrant Cloud · Resend · PostHog.</p>
    <p class="revenue-grid__cost">~$0/month for low-volume usage.</p>
  </li>
  <li>
    <h4>Mobile API backend</h4>
    <p>Cloudflare Workers · Supabase · Logto · R2 · Sentry.</p>
    <p class="revenue-grid__cost">~$0/month within free limits.</p>
  </li>
  <li>
    <h4>Static portfolio / docs</h4>
    <p>GitHub Pages · Cloudflare CDN · Cloudflare Turnstile · GoatCounter.</p>
    <p class="revenue-grid__cost">~$0/month, forever.</p>
  </li>
  <li>
    <h4>Homelab control plane</h4>
    <p>Tailscale · Cloudflare Tunnel · Grafana OSS · Meilisearch · PocketBase · ntfy.</p>
    <p class="revenue-grid__cost">Hardware cost only.</p>
  </li>
  <li>
    <h4>Internal analytics dashboard</h4>
    <p>PostHog OSS · Grafana OSS · Cloudflare R2 · Supabase · Metabase.</p>
    <p class="revenue-grid__cost">~$0/month self-hosted.</p>
  </li>
</ul>

## Free doesn't mean risk-free

The biggest gotcha with free tiers is not the headline allowance — it's what happens once you cross it, and whether the provider can charge you without explicit consent.

<aside class="callout callout--important" aria-label="Important">
  <p class="callout__label">Read the billing terms</p>
  <p>Some providers require a payment method up-front and will charge for overages above the free ceiling. If you cannot tolerate surprise billing, prefer entries tagged <strong>No card</strong> and <strong>Open source</strong>. Always check the <em>What happens when you cross the limit?</em> line on each card before depending on it.</p>
</aside>

## Compare free tiers

A scannable summary of the entries below. Filter the cards above for the same answer, in context.

<div class="table-wrap">
<table class="resource-table">
  <thead>
    <tr>
      <th scope="col">Service</th>
      <th scope="col">Category</th>
      <th scope="col">Free tier</th>
      <th scope="col">Card</th>
      <th scope="col">Self-host</th>
      <th scope="col">Commercial</th>
      <th scope="col">Verified</th>
    </tr>
  </thead>
  <tbody>
    {%- for g in _groups -%}
      {%- assign _group_items = _items | where: "group", g.id -%}
      {%- for r in _group_items -%}
        <tr>
          <th scope="row"><a href="{{ r.url }}" rel="noopener">{{ r.name }}</a></th>
          <td>{{ g.title }}</td>
          <td>{{ r.free_tier | truncate: 90 }}</td>
          <td>
            {%- case r.card_required -%}
              {%- when "no" -%}<span class="badge badge--ok">No card</span>
              {%- when "yes" -%}<span class="badge badge--warn">Card</span>
              {%- else -%}—
              {%- endcase -%}
          </td>
          <td>
            {%- case r.self_host -%}
              {%- when "yes" -%}<span class="badge badge--ok">Yes</span>
              {%- when "partial" -%}<span class="badge badge--neutral">Partial</span>
              {%- else -%}<span class="badge badge--neutral">No</span>
              {%- endcase -%}
          </td>
          <td>
            {%- case r.commercial_use -%}
              {%- when "yes" -%}<span class="badge badge--ok">Yes</span>
              {%- when "review" -%}<span class="badge badge--neutral">Review</span>
              {%- else -%}—
              {%- endcase -%}
          </td>
          <td><time datetime="{{ r.as_of | date: '%Y-%m-%d' }}">{{ r.as_of | date: "%b %Y" }}</time></td>
        </tr>
      {%- endfor -%}
    {%- endfor -%}
  </tbody>
</table>
</div>

## Recently changed

Notable updates to this page since the last bulk re-check.

<div class="changelog">
  <article class="changelog__entry">
    <h4><time datetime="2026-09-25">September 25, 2026</time> — bulk re-verification pass</h4>
    <ul>
      <li>Updated Fly.io entry — current offering is a limited <strong>2-hour / 7-day free trial</strong>, not the older 3-VM / 2,340-hour allowance.</li>
      <li>Updated Supabase free plan — projects pause after one week of inactivity; 2 active projects per org.</li>
      <li>Added AI &amp; LLMs section with Gemini, Groq, OpenRouter, Hugging Face, Together.ai, Cohere, Mistral, Ollama, LM Studio, Pinecone, Qdrant and Chroma.</li>
      <li>Added Storage &amp; CDN, Email &amp; communication, Search, Background jobs, Security, Testing, Developer tools, Maps &amp; location, Free APIs, Student benefits and Open-source alternatives sections.</li>
      <li>Added tier type, credit-card requirement, commercial-use, "over limit" and "not ideal for" metadata to every entry.</li>
    </ul>
  </article>
</div>

## The full directory

{% for g in _groups %}
{%- assign _group_items = _items | where: "group", g.id %}
<section class="resource-group" aria-labelledby="res-{{ g.id }}" data-filter-group>
  <h2 class="resource-group__title" id="res-{{ g.id }}">{% include icon.html name=g.icon %}{{ g.title }} <span class="muted">{{ _group_items.size }}</span></h2>
  <ul class="resource-grid">
    {%- for r in _group_items %}<li>{% include resource-card.html item=r %}</li>{% endfor %}
  </ul>
</section>
{%- endfor -%}
<div data-resource-empty hidden>{% include state.html icon="search" title="Nothing matches that filter" body="Try a broader term such as “postgres” or “auth”, or untick a filter pill above." %}</div>

{%- if _removed and _removed.size > 0 %}
<section class="resource-removed" aria-label="Removed free tiers">
  <h2 class="resource-group__title">{% include icon.html name="alert" %}Removed / no longer free <span class="muted">{{ _removed.size }}</span></h2>
  <p class="muted">We don't silently delete entries. This is the historical record of services whose free offering has materially changed or been retired.</p>
  <div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th scope="col">Service</th>
        <th scope="col">Previous offer</th>
        <th scope="col">Why removed</th>
        <th scope="col">Date</th>
      </tr>
    </thead>
    <tbody>
      {%- for r in _removed -%}
      <tr>
        <th scope="row">{{ r.name }}</th>
        <td>{{ r.previous_offer }}</td>
        <td>{{ r.why_removed }}</td>
        <td><time datetime="{{ r.date | date: '%Y-%m-%d' }}">{{ r.date | date: "%b %Y" }}</time></td>
      </tr>
      {%- endfor -%}
    </tbody>
  </table>
  </div>
</section>
{%- endif %}

## Frequently asked questions

<details class="faq">
  <summary><h3>What does "free" mean on this page?</h3></summary>
  <p>Each entry is tagged as one of <strong>free forever</strong>, <strong>free tier</strong>, <strong>free trial</strong> or <strong>open source</strong>. Free forever means you can stay on the free plan indefinitely. Free tier means there is a monthly ceiling that resets each cycle. Free trial means the free allowance is time-boxed or credits-based. Open source means you can also run it on your own infrastructure.</p>
</details>

<details class="faq">
  <summary><h3>Which services require a credit card?</h3></summary>
  <p>Use the <em>No credit card</em> pill above to keep only entries that do not need a payment method to sign up. The same filter is shown in the comparison table as the <em>Card</em> column.</p>
</details>

<details class="faq">
  <summary><h3>Which entries allow commercial use?</h3></summary>
  <p>Use the <em>Commercial OK</em> pill, or the <em>Commercial</em> column in the comparison table. Entries tagged <em>Review</em> are free but require reading the license terms before shipping a paid product.</p>
</details>

<details class="faq">
  <summary><h3>Which entries can I self-host?</h3></summary>
  <p>Use the <em>Self-hostable</em> pill, or the <em>Self-host</em> column. <em>Partial</em> means an open-source runtime or a free self-hosted runner is available but the canonical product is managed.</p>
</details>

<details class="faq">
  <summary><h3>What happens when I exceed the limit?</h3></summary>
  <p>Every entry has an <em>Over limit</em> line in the card. The most common patterns are: <em>Service pauses</em> (Supabase), <em>Requests return errors</em> (Cloudflare Workers, Upstash), <em>Pay-as-you-go</em> (some free trials) and <em>Storage throttled</em>. Read those lines before depending on a service.</p>
</details>

<details class="faq">
  <summary><h3>Why isn't this just a list of 400 "maybe free" services?</h3></summary>
  <p>The audit that drives this page treats <em>free</em> as a contract: a labelled allowance, an explicit over-limit behaviour and a verified date. Anything where those three aren't all true would not be useful to you.</p>
</details>

<section class="resource-report">
  <h2 class="eyebrow">Notice a discrepancy?</h2>
  <p>Is a free tier gone, or did a company pull a bait-and-switch? <a href="https://github.com/ambicuity/Tech-Blog/issues/new?template=submit-tool.yml">Open an issue</a> and it will be corrected or removed.</p>
</section>