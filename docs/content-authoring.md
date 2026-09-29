# Content authoring guide

How to add an article to [blog.riteshrana.engineer](https://blog.riteshrana.engineer).
Written for people and for automated authors (such as the Muse content
agent): if you follow this document, you never need to touch layouts, CSS,
navigation or any other site code. The site discovers the article, lists it
everywhere it belongs, and publishes it.

What to write, and how to shape it (topic mix, titles, backlog), is in
[editorial-guide.md](editorial-guide.md).

The rules below are enforced by `_plugins/content_contract.rb`. CI runs them on
every pull request and before every deploy; an article that breaks a rule
cannot go live.

---

## 1. Where articles go

One folder per article:

```text
content/posts/
└── idempotent-webhook-handlers/     ← the folder name is the slug
    ├── index.md                     ← front matter + Markdown body
    ├── cover.webp                   ← optional cover image
    └── flow.svg                     ← any other images the article uses
```

The article is published at **`/posts/<slug>/`**, and its files at
`/posts/<slug>/<file>`.

That is the whole integration. Adding the folder automatically updates the
home page, the archive, the topic (category) and tag pages, search, related
articles, the RSS feed and the sitemap.

> `content/posts/idempotent-webhook-handlers/` is a complete, working example
> (kept as a draft). Copy its structure.

Older articles live in `_posts/YYYY-MM-DD-slug.md`. They keep working and keep
their URLs; do not add new articles there.

## 2. Front matter

`index.md` starts with a YAML front matter block:

```yaml
---
title: "Idempotent Webhook Handlers: Surviving At-Least-Once Delivery"
description: >-
  Webhook providers retry, and some deliver the same event twice. A practical
  pattern for processing each event exactly once.
date: 2026-09-28 10:00:00 +0000
author: ritesh
categories: [Distributed Systems, Reliability]
tags: [idempotency, webhooks, postgresql, python]
kind: Guide
draft: false
cover:
  image: cover.webp
  alt: Two deliveries of the same webhook event; the second is acknowledged as already processed.
---
```

### Required

| Field | Rules |
| :--- | :--- |
| `title` | Plain text. **Quote it** if it contains `: ` (a colon followed by a space) — otherwise the YAML is invalid and the build fails. Aim for under 70 characters. |
| `description` | 1–2 sentences, 120–200 characters. Used under the title, on cards, in search results and as the meta description. Not a copy of the first paragraph. |
| `date` | Publication time: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS +0000` (UTC). A future date keeps the article out of the site until the first build after that time (the site builds on every push to `main`, or on demand). |
| `author` | An author key from `_data/authors.yml` (currently `ritesh`). Never invent a byline. |
| `categories` | A list of 1–2 subjects **from the list in section 5**. The first is the primary subject; it sets the breadcrumb and card label. |
| `tags` | A list of 3–8 tags (see section 5). |

### Optional

| Field | Meaning |
| :--- | :--- |
| `updated` | Date of the last substantive revision (same format as `date`, not earlier than it). Shown as "Updated …". |
| `kind` | One of `Guide`, `Case Study`, `Deep Dive`, `Comparison`, `Opinion`, `Scenario`. If omitted it is inferred from the title. `Case Study` is only for real, sourced events. |
| `scenario` | `illustrative` when the article narrates a made-up or composite situation ("the alert fired at 03:17", "our service"). The page then shows an "Illustrative scenario" notice and the kind becomes `Scenario`. See *Accuracy*. |
| `draft` | `true` keeps the article out of production. See section 7. Default `false`. |
| `featured` | `true`/`false`. Stored for editorial use; no page uses it yet. To put an article in the home page's featured slot, use `pin`. |
| `pin` | `true` puts the article in the home page's featured slot. Use sparingly. |
| `cover` | `image` (a file in the article folder) and `alt` (required when `cover` is set). Also used as the social share image. |
| `canonical_url` | Absolute `https://` URL, only when the article was first published elsewhere. |

Do not set `slug`, `layout` or `permalink`. The folder name is the slug; if
`slug` is present it must equal the folder name.

## 3. Slug rules

- Lowercase letters, digits and single hyphens: `^[a-z0-9]+(-[a-z0-9]+)*$`
- Derived from the title, without dates or stop-word padding:
  `idempotent-webhook-handlers`, not `2026-09-28-how-to-build-idempotent-webhook-handlers-a-guide`
- At most 80 characters
- Unique across all articles, old and new. CI fails on a duplicate.
- **Never change a published slug.** The slug is the URL; changing it breaks
  every existing link.

## 4. Body, images and links

### Headings

The title is already the page's `<h1>`. Start sections at `##`, use `###` for
subsections, and do not skip levels. `##` and `###` headings build the table of
contents automatically.

### Code blocks

Always use fenced blocks with a language:

````markdown
```python
def handler(event): ...
```
````

Common languages: `python`, `go`, `rust`, `java`, `javascript`, `typescript`,
`bash` (commands), `console`/`text` (output), `yaml`, `json`, `sql`,
`dockerfile`, `terraform`, `promql`. Every block gets a language label and a
copy button automatically. Keep lines under about 100 characters; longer lines
scroll horizontally.

For diagrams, a fenced `mermaid` block is rendered as a diagram.

### Callouts

```markdown
> [!NOTE]
> Context the reader should know.

> [!TIP]
> A recommendation.

> [!WARNING]
> Something that causes data loss, outages or security problems.

> [!IMPORTANT]
> A hard requirement.

> [!RESULT]
> The measured outcome of a change.
```

A plain `>` blockquote stays a quotation.

### Tables and math

GitHub-style tables work and scroll on small screens. Math uses `$$ … $$`
(inline or display).

### Images

- Put image files in the article folder and reference them **relatively**:
  `![Request flow through the gateway](flow.svg)`
- Formats: WebP (preferred), AVIF, PNG, JPEG, GIF, SVG. Aim for under 500 KiB;
  over 5 MiB fails CI.
- Every image needs alt text describing what it shows. Missing alt text is a
  warning; a missing file is an error.
- Cover images: 1200×630, WebP.

### Internal links

Link to other articles by URL path: `[Idempotent operations](/posts/idempotent-operations-in-distributed-systems-a-practical-guide/)`.
CI checks every internal link; a broken one fails the build. Two to four
relevant internal links per article is a good target.

### References

End with a `## References` section listing primary sources: official docs,
RFCs, specifications, postmortems, papers. Write each one as a Markdown link —
a bare URL renders as plain, unclickable text:

```markdown
## References

- Chris Richardson, [Pattern: Transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html), *microservices.io*
- [PostgreSQL: The locking clause](https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE)
```

Only cite pages you have opened, and only for what they actually say. Every
external link in a changed article is requested in CI: a page that returns 404
or 410, or a host that does not exist, fails the pull request. Links to other
sites get an "external" indicator automatically.

### Accuracy

Do not invent measurements, incidents, quotations or sources. If a number is
illustrative, say so. Every claim a reader could check should link to the
source that supports it.

Narratives are welcome as a teaching device, but never present an invented
incident as something that happened. Either write it as a hypothetical
("Consider a service that…") or keep the first-person story and set
`scenario: illustrative`. Do not name real products, vendors or companies as
the cause of an invented incident, and do not list a scenario's figures as
"evidence". Code and prose must agree: if the text says events
are keyed by order ID, the code must key them by order ID.

Never leave placeholders for later in the text — `[CLAIM:...]`, `[TODO]`,
`[TBD]`, `[INSERT ...]`, `[FIXME]` fail validation. (Placeholders inside code,
such as `YOUR_QUEUE_URL`, are fine.)

## 5. Categories and tags

### Categories

Use 1–2 of these exact names (defined in `_data/taxonomy.yml`):

`AI` · `Kubernetes` · `Distributed Systems` · `Reliability` · `DevOps` ·
`Platform Engineering` · `Cloud Computing` · `Performance` · `Python` ·
`Security` · `Software Engineering` · `Database`

An unknown category fails validation. New subjects need a human decision:
add them to `_data/taxonomy.yml` in a separate change.

### Tags

- Lowercase and hyphenated: `graceful-shutdown`, `postgresql`, `rate-limiting`
- 3–8 per article, specific rather than generic (`kafka`, not `technology`)
- Reuse existing tags; the full list is on `/tabs/tags/`

Tags are normalized at build time (for example `k8s` → `kubernetes`,
`Platform Engineering` → `platform-engineering`), and filler tags such as
`tech` or `software` are dropped. Write them canonically in the first place.

## 6. Publishing from JSON (automated authors)

Instead of writing files by hand, produce one JSON package and run:

```bash
ruby scripts/publish_article.rb article.json --dry-run   # validate only
ruby scripts/publish_article.rb article.json             # write content/posts/<slug>/
ruby scripts/publish_article.rb article.json --json      # machine-readable result
```

```json
{
  "title": "Kafka Rebalances: Why Consumers Stall",
  "description": "What happens to in-flight messages during a consumer-group rebalance, and how to keep processing safe.",
  "date": "2026-10-05T09:00:00Z",
  "author": "ritesh",
  "categories": ["Distributed Systems"],
  "tags": ["kafka", "consumers", "reliability"],
  "kind": "Guide",
  "draft": true,
  "cover": { "image": "cover.webp", "alt": "Timeline of a consumer-group rebalance" },
  "content": "Rebalances pause consumption…\n\n## Why it happens\n\n…",
  "images": [
    { "name": "cover.webp", "path": "images/cover.webp" },
    { "name": "timeline.png", "base64": "iVBORw0KGgo…" }
  ]
}
```

- `slug` is optional; by default it is derived from the title.
- `date` defaults to now (UTC); `author` defaults to `ritesh`; `draft` to `false`.
- `images[].path` is relative to the JSON file; use `base64` to inline bytes.
- The script writes valid YAML itself (colons in titles are safe), validates
  the result against this contract including duplicate slugs, and writes
  **nothing** if anything fails. It refuses to overwrite an existing article
  unless `--force` is given.

Exit status `0` means the bundle was written and is valid.

## 7. Drafts and publication workflow

1. **Draft** — create the article with `draft: true`. It is validated and built
   by CI, but it appears nowhere in production: no page, feed, sitemap,
   search entry or listing.
2. **Preview** — `bundle exec jekyll serve --drafts` renders drafts locally.
   Pull requests also upload a preview build that includes drafts (Actions
   run → artifact `site-preview-with-drafts`).
3. **Publish** — set `draft: false` (or remove the line) and merge. The deploy
   workflow validates, tests, builds, checks links and publishes.

Recommended flow for automated authors:

```text
create branch  →  add content/posts/<slug>/  →  open pull request
      →  Content CI (validate, test, build, links)  →  review / auto-merge
      →  merge to main  →  deploy
```

Give an automated author credentials scoped to **this repository only**
(a GitHub App with Contents and Pull requests: read and write is preferable
to a personal token), and protect `main` so changes arrive through pull
requests that pass Content CI.

## 8. Validation commands

```bash
bundle install                                   # once

ruby scripts/validate_content.rb                 # every article: errors fail, warnings don't
ruby scripts/validate_content.rb content/posts/my-article
ruby scripts/validate_content.rb --json          # machine-readable
ruby scripts/check_external_links.rb content/posts/my-article   # request every external link
ruby scripts/check_external_links.rb --changed-since origin/main

bundle exec ruby test/plugins_test.rb            # full test suite
bundle exec jekyll build                         # production build (drafts excluded)
bundle exec jekyll serve --drafts                # local preview including drafts
```

### What fails the build

- Missing or invalid front matter (including unquoted `: ` in a title)
- Missing `title`, `description`, `date`, `author`, `categories` or `tags`
- Invalid `date`/`updated`, or `updated` earlier than `date`
- Unknown author or category
- Invalid or duplicate slug
- `draft`, `featured` or `pin` that is not `true`/`false`
- A referenced image that is missing, outside the article folder, of an
  unsupported type, or over 5 MiB
- `cover` without `image` or `alt`
- A leftover placeholder in the text (`[CLAIM:...]`, `[TODO]`, `[INSERT ...]`, …)
- A code block that lost its ``` fences (a line that reads only `yaml`, `bash`, …)
- A broken internal link (checked on the built site)
- In pull requests: an external link in a changed article that returns 404/410
  or whose host does not exist (`scripts/check_external_links.rb`)

### What only warns

Description or title length, tag count, non-canonical tags, images without
alt text, images over 500 KiB, a level-1 heading in the body, no
`## References` section, bare URLs under References, no links to other
articles, a formulaic title (see [editorial-guide.md](editorial-guide.md#titles)), and external links that could not be verified (403, 429, 5xx,
timeouts — often bot protection, so check them by hand).

## 9. Checklist

- [ ] `content/posts/<slug>/index.md`, slug rules followed, slug unused
- [ ] Required front matter present; title quoted if it contains `: `
- [ ] Categories from the list; 3–8 canonical tags
- [ ] Sections start at `##`; code fences have languages
- [ ] Images in the folder, referenced relatively, with alt text
- [ ] 2–4 internal links; a References section of `[Title](url)` links to primary sources
- [ ] No invented numbers, incidents or quotes; code matches what the text says
- [ ] A made-up incident narrative has `scenario: illustrative`
- [ ] No `[CLAIM:...]` / `[TODO]` placeholders left in the text
- [ ] `ruby scripts/validate_content.rb` passes
- [ ] `ruby scripts/check_external_links.rb content/posts/<slug>` reports no broken links
