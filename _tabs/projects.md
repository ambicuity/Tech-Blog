---
layout: page
icon: fas fa-code
order: 7
title: Projects
wide: true
eyebrow: Engineering portfolio
lede: Open-source tools, infrastructure modules and experiments. Everything here links to real source code; live deployments are marked.
---
{%- assign _featured = site.data.projects | where: "featured", true -%}
{%- assign _rest = site.data.projects | where_exp: "p", "p.featured != true" -%}
<section class="section section--flush" aria-labelledby="featured-projects">
  <h2 class="section__title" id="featured-projects">Featured</h2>
  <ul class="project-grid project-grid--featured">
    {%- for proj in _featured %}<li>{% include project-card.html item=proj %}</li>{% endfor %}
  </ul>
</section>
<section class="section" aria-labelledby="more-projects">
  <h2 class="section__title" id="more-projects">More projects</h2>
  <ul class="project-grid">
    {%- for proj in _rest %}<li>{% include project-card.html item=proj %}</li>{% endfor %}
  </ul>
  <p class="section__more"><a class="arrow-link" href="{{ site.contact.github }}" rel="me noopener">Everything else on GitHub {% include icon.html name="arrow-right" %}</a></p>
</section>
