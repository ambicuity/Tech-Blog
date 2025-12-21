---
layout: default
title: blog
---

# Tech Blog

Welcome to my automated technical blog! Here you'll find articles on various technology topics.

## Recent Posts

{% assign sorted_posts = site.posts | sort: 'date' | reverse %}
{% for post in sorted_posts %}
  <article class="post">
    <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
    <p class="post-meta">
      <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%B %d, %Y" }}</time>
      {% if post.author %} • {{ post.author }}{% endif %}
    </p>
    {% if post.excerpt %}
      <p>{{ post.excerpt | strip_html | truncatewords: 50 }}</p>
    {% endif %}
    {% if post.tags %}
      <p class="tags">
        Tags: 
        {% for tag in post.tags %}
          <span class="tag">{{ tag }}</span>{% unless forloop.last %}, {% endunless %}
        {% endfor %}
      </p>
    {% endif %}
    <p><a href="{{ post.url | relative_url }}">Read more →</a></p>
  </article>
  <hr>
{% endfor %}

{% if site.posts.size == 0 %}
  <p>No posts yet. Check back soon!</p>
{% endif %}
