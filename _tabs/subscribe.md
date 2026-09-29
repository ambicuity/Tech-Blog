---
layout: page
icon: fas fa-envelope
order: 6
title: Newsletter
permalink: /newsletter/
wide: true
eyebrow: By email
lede: Get each new article by email. No spam — just code and architecture.
---
<div class="newsletter-page">
  <div class="newsletter-page__form">
    <h2 class="newsletter__title">Subscribe</h2>
    <p class="newsletter__body">One short email each time a new article is published, roughly once a week.</p>
    {% include subscribe-form.html id="newsletter-page" %}
  </div>
  <div class="newsletter-page__details">
    <h2 class="eyebrow">What you'll get</h2>
    <ul class="newsletter__points">
      <li>{% include icon.html name="check" %}<span>Kubernetes &amp; cloud native</span></li>
      <li>{% include icon.html name="check" %}<span>Python &amp; scalable architecture</span></li>
      <li>{% include icon.html name="check" %}<span>DevOps best practices</span></li>
      <li>{% include icon.html name="check" %}<span>Career growth for engineers</span></li>
    </ul>
    <h2 class="eyebrow">Who it's for</h2>
    <p>Platform, infrastructure and backend engineers who would rather read one careful write-up than ten hot takes.</p>
    <h2 class="eyebrow">The fine print</h2>
    <p>Your address is stored on my own server and used only to send new articles. Every email has a one-click unsubscribe link.</p>
    <p class="muted">Prefer feeds? Subscribe via <a href="{{ '/feed.xml' | relative_url }}">RSS</a>, or browse past articles in the <a href="{{ '/tabs/archives/' | relative_url }}">archive</a>.</p>
  </div>
</div>
