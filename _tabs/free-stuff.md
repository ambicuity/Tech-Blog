---
layout: page
icon: fas fa-gift
order: 9
title: Free Dev Stuff
permalink: /free-stuff/
wide: true
eyebrow: Resources
lede: An opinionated shortlist of developer-first free tiers and self-hostable tools that work for prototypes, homelabs and MVPs — without surprise billing. Not a directory of 400 “maybe free” services.
---
{%- assign _items = site.data.resources.items -%}
<aside class="callout callout--warning resource-disclaimer" aria-label="Warning">
  <p class="callout__label">Check before you build</p>
  <p>Free tiers change without notice. Every entry shows when its details were written down — confirm limits on the official pricing page before depending on them.</p>
</aside>

<div class="resource-toolbar" hidden data-resource-controls>
  <label class="visually-hidden" for="resource-filter">Filter resources</label>
  <input class="input input--sm" id="resource-filter" type="search" placeholder="Filter by name or use case…" autocomplete="off" data-resource-filter>
  <p class="visually-hidden" role="status" aria-live="polite" data-resource-status></p>
</div>

{%- for g in site.data.resources.groups %}
{%- assign _group_items = _items | where: "group", g.id %}
<section class="resource-group" aria-labelledby="res-{{ g.id }}" data-filter-group>
  <h2 class="resource-group__title" id="res-{{ g.id }}">{% include icon.html name=g.icon %}{{ g.title }} <span class="muted">{{ _group_items.size }}</span></h2>
  <ul class="resource-grid">
    {%- for r in _group_items %}<li>{% include resource-card.html item=r %}</li>{% endfor %}
  </ul>
</section>
{%- endfor %}
<div data-resource-empty hidden>{% include state.html icon="search" title="Nothing matches that filter" body="Try a broader term such as “postgres” or “auth”." %}</div>

<section class="resource-report">
  <h2 class="eyebrow">Notice a discrepancy?</h2>
  <p>Is a free tier gone, or did a company pull a bait-and-switch? <a href="https://github.com/ambicuity/Tech-Blog/issues/new">Open an issue</a> and it will be corrected or removed.</p>
</section>
