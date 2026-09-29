---
layout: page
icon: fas fa-water
order: 3
title: Courses
permalink: /courses/
wide: true
eyebrow: Courses
lede: Three free, open-source courses, each on its own site — hundreds of lessons with runnable code, built from first principles. Below them are the shorter notes that started here on the blog.
---
{%- assign _notes = site.data.deep_dives | where: "listed", true -%}
<section aria-labelledby="full-courses">
  <h2 class="visually-hidden" id="full-courses">Full courses</h2>
  <ul class="course-grid">
    {%- for c in site.data.course_sites %}
    <li>{% include course-card.html item=c %}</li>
    {%- endfor %}
  </ul>
</section>

<section class="section notes-section" aria-labelledby="companion-notes">
  <div class="section__head">
    <div>
      <h2 class="section__title" id="companion-notes">Companion notes</h2>
      <p class="section__desc">Long-form essays written on this blog before the courses existed. They stay online, but the courses above are the maintained, complete versions.</p>
    </div>
  </div>
  <ul class="shelf shelf--library">
    {%- for dd in _notes %}
    <li>{% include deep-dive-card.html item=dd %}</li>
    {%- endfor %}
  </ul>
</section>
