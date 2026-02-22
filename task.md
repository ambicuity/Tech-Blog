# Tech Blog Automation Tasks

- [x] **Brave Search Integration**
    - [x] Create `scripts/brave_search.py` to fetch tech news <!-- id: 0 -->
    - [x] Test search functionality locally <!-- id: 1 -->

- [x] **Content Generation Logic**
    - [x] Modify `scripts/generate_blog.py` to consume Brave Search results <!-- id: 2 -->
    - [x] Improve prompting for "originality" and "non-repetitive" content <!-- id: 3 -->
    - [x] Ensure unique filenames/titles <!-- id: 4 -->

- [x] **Automation & CI/CD**
    - [x] Update `.github/workflows/generate-blog.yml` with `BRAVE_API_KEY` <!-- id: 5 -->

- [x] **Configuration & UI**
    - [x] Revert `_config.yml` to original branding <!-- id: 6 -->

- [x] **Documentation**
    - [x] Create a guide/snippet on how to add `BRAVE_API_KEY` to GitHub Secrets <!-- id: 7 -->

- [x] **Deployment**
    - [x] Push branding revert to GitHub <!-- id: 8 -->

- [x] **Validation**
    - [x] Create `scripts/validate_posts.py` to check code blocks <!-- id: 9 -->
    - [x] Integrate validation into GitHub Actions workflow <!-- id: 10 -->

- [x] **Batch Formatting**
    - [x] Create `scripts/format_posts.py` to auto-fix all posts <!-- id: 11 -->
    - [x] Run formatter on existing posts <!-- id: 12 -->
    - [x] Update workflow to auto-format before deploy <!-- id: 13 -->
