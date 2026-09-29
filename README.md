# Ritesh Rana Tech Blog

Welcome to the source code for my personal engineering blog, where I share deep dives into **Kubernetes**, **System Design**, **DevOps**, and **Software Engineering** best practices.

**Live Site:** [blog.riteshrana.engineer](https://blog.riteshrana.engineer)

## 🚀 About the Blog

This blog is built for engineers, by an engineer. It serves as a knowledge base for solving complex infrastructure problems, understanding distributed systems, and mastering modern CI/CD workflows.

### Key Topics
- **Kubernetes & Orchestration**: Advanced patterns, security, and performance tuning.
- **System Design**: Architectural decisions, scalability, and reliability.
- **DevOps**: CI/CD pipelines, Infrastructure as Code (IaC), and observability.
- **Backend Engineering**: Python, Go, and database optimization.

## 🛠️ Tech Stack

This site is statically generated using **Jekyll** and hosted on **GitHub Pages**, ensuring speed, security, and reliability.

- **Theme**: Custom, maintained in this repository (see *Frontend architecture* below)
- **Comments**: Giscus (GitHub Discussions)
- **Analytics**: Google Analytics 4
- **Newsletter**: Custom PHP Integration (Self-Hosted)
- **Deployment**: GitHub Actions
- **Content pipeline**: lives in a separate private repository and publishes posts here; every post passes this repo's front-matter guard before it can deploy

## 💻 Local Development

To run this blog locally on your machine:

1.  **Prerequisites**: Ensure you have Ruby and Bundler installed.
2.  **Install Dependencies**:
    ```bash
    bundle install
    ```
3.  **Run Server**:
    ```bash
    bundle exec jekyll serve
    ```
4.  **Preview**: Open `http://localhost:4000` in your browser.
5.  **Test** (also runs in CI before every deploy):
    ```bash
    bundle exec ruby test/plugins_test.rb
    JEKYLL_ENV=production bundle exec jekyll build && bundle exec htmlproofer _site --disable-external
    ```

## 🧱 Frontend architecture

No theme gem and no JS framework — static HTML, one stylesheet, two small scripts.

| Path | What lives there |
| :--- | :--- |
| `_sass/_tokens.scss` | Design tokens: color (light "paper" / dark "graphite"), type scale, spacing, radii, motion. Change values here, never in components. |
| `_sass/_*.scss` | `base` → `layout` (header, menu, footer) → `components` → `prose` (article body) → `syntax` → `pages` → `print` |
| `_layouts/` | `default`, `home`, `post`, `page`, `course`, `archives`, `categories`, `tags`, `taxonomy` (category/tag pages), `redirect` |
| `_includes/` | One file per component: `post-card`, `post-meta`, `toc`, `breadcrumbs`, `pager`, `pagination`, `newsletter-cta`, `subscribe-form`, `course-card`, `project-card`, `resource-card`, `state` … |
| `_plugins/taxonomy.rb` | Normalizes tags/categories on every build using `_data/taxonomy.yml` (so pipeline posts can't reintroduce duplicates) and emits redirects from `_data/legacy_redirects.yml`. |
| `_plugins/content.rb` | Build-time HTML enhancement: code-block labels + copy buttons, heading anchors, callouts, scrollable tables, lazy images; summaries, reading time, related posts. |
| `_plugins/courses.rb` | Structure for the in-blog notes under `courses/` (layout, chapter order from each syllabus, prev/next, links to the full courses). |
| `_plugins/search_index.rb` | Generates `/assets/js/data/search.json` for the ⌘K / Ctrl K search dialog. |
| `assets/js/site.js`, `search.js` | Theme toggle, dialogs, copy, scroll-spy, forms, filters; search is loaded on first use. |
| `_data/` | `taxonomy`, `course_sites` (the standalone courses and which articles link to them), `start_here` (the home page reading path), `deep_dives` (in-blog notes), `projects`, `resources`, `nav`, `icons` (Lucide). |

**Writing posts.** Front matter needs `title`, `date`, `categories` (1–2 from `_data/taxonomy.yml`, primary first) and `tags`. Quote titles that contain a colon. Optional: `description` (otherwise the first paragraph is used), `kind` (Guide, Case Study, Deep Dive, Comparison, Opinion — otherwise inferred from the title), `pin: true`, `last_modified_at`. Callouts: `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`, `> [!IMPORTANT]`, `> [!RESULT]`.

## 📬 Newsletter

I run a self-hosted newsletter to share the latest articles.
- **Subscribe**: Form available on the [home page](https://blog.riteshrana.engineer).
- **Privacy**: No tracking pixels, no third-party data sharing. Just engineering content.

## 👤 Author

**Ritesh Rana**  
*Software Engineer*

- **Website**: [riteshrana.engineer](https://riteshrana.engineer)
- **Contact**: [contact@riteshrana.engineer](mailto:contact@riteshrana.engineer)
- **LinkedIn**: [riteshengineer](https://www.linkedin.com/in/riteshengineer/)
- **GitHub**: [ambicuity](https://github.com/ambicuity)

---
© 2026 Ritesh Rana. All Rights Reserved.
