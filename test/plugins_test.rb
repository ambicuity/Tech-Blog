# frozen_string_literal: true

# Tests for the theme's build plugins (_plugins/).
#
#   bundle exec ruby test/plugins_test.rb
#
# Unit tests exercise the pure functions; SiteBuildTest builds the whole site
# once into a temp directory and checks the invariants the theme relies on.

require "minitest/autorun"
require "jekyll"
require "json"
require "tmpdir"
require "yaml"
require "date"

ROOT = File.expand_path("..", __dir__)
Dir[File.join(ROOT, "_plugins", "*.rb")].sort.each { |f| require f }

class TaxonomyTest < Minitest::Test
  CONFIG = YAML.safe_load_file(File.join(ROOT, "_data", "taxonomy.yml"))
  ALIASES = CONFIG["tag_aliases"].transform_keys(&:to_s)
  DROP = CONFIG["tag_drop"].map(&:to_s)

  def norm(tag) = TechBlog::Taxonomy.normalize_tag(tag, ALIASES, DROP)

  def test_case_and_spacing_are_normalized
    assert_equal "kubernetes", norm("Kubernetes")
    assert_equal "platform-engineering", norm("platform engineering")
    assert_equal "platform-engineering", norm("platform-engineering")
    assert_equal "best-practices", norm(" Best  Practices ")
  end

  def test_semantic_aliases_merge
    assert_equal "kubernetes", norm("k8s")
    assert_equal "postgresql", norm("postgres")
    assert_equal "io-bound", norm("i/o-bound")
    assert_equal "python", norm("python3.14")
    assert_equal "canary-deployments", norm("canary-deployment")
  end

  def test_symbol_only_tags_are_dropped
    assert_nil norm("???")
    assert_nil norm("🚀")
  end

  def test_filler_tags_are_dropped
    %w[tech software engineering 2026].each { |t| assert_nil norm(t), t }
  end

  def test_placeholder_categories_fall_back_to_default
    assert_equal ["Software Engineering"], TechBlog::Taxonomy.normalize_categories(%w[Tech Engineering], CONFIG)
  end

  def test_categories_are_canonical_and_capped_at_two
    assert_equal ["Kubernetes", "Python"],
                 TechBlog::Taxonomy.normalize_categories(%w[kubernetes python performance], CONFIG)
    assert_equal ["Platform Engineering"], TechBlog::Taxonomy.normalize_categories(["Platform-Engineering"], CONFIG)
  end
end

# Pre-deploy guard for posts written by the content pipeline. A post that fails
# here would otherwise publish broken: invalid YAML silently drops the whole
# front matter (empty title, date-prefixed URL, build date), and a model-invented
# date publishes the post in the wrong year.
class PostFrontMatterTest < Minitest::Test
  # The pipeline names files with the authoritative date (today, or POST_DATE for
  # backfills), so the front-matter date must agree. Posts before this date come
  # from an older generator and are grandfathered.
  DATE_CHECK_FROM = "2026-01-01"
  AUTHORS = YAML.safe_load_file(File.join(ROOT, "_data", "authors.yml")).keys

  Dir[File.join(ROOT, "_posts", "*.md")].sort.each do |path|
    name = File.basename(path)

    define_method("test_front_matter_#{name.tr('^a-zA-Z0-9', '_')}") do
      source = File.read(path)
      match = source.match(/\A---\s*\n(.*?)\n---\s*\n/m)
      assert match, "#{name}: missing front matter block"

      data = begin
        YAML.safe_load(match[1], permitted_classes: [Date, Time])
      rescue Psych::SyntaxError => e
        flunk "#{name}: front matter is not valid YAML (quote titles that contain ': '): #{e.message}"
      end

      assert data["title"].is_a?(String) && !data["title"].strip.empty?, "#{name}: title is missing"
      refute_nil data["date"], "#{name}: date is missing"
      assert Array(data["categories"]).any?, "#{name}: categories are missing"
      assert data.key?("tags"), "#{name}: tags are missing"
      assert_includes AUTHORS, data["author"].to_s, "#{name}: unknown author" if data.key?("author")

      file_date = name[0, 10]
      if file_date >= DATE_CHECK_FROM
        fm_date = data["date"].respond_to?(:strftime) ? data["date"].strftime("%Y-%m-%d") : data["date"].to_s[0, 10]
        assert_equal file_date, fm_date, "#{name}: front-matter date does not match the file name"
      end
    end
  end
end

class ContentTest < Minitest::Test
  def enhance(html) = TechBlog::Content.enhance(html)

  def test_rouge_block_gets_label_and_copy_button
    html = '<div class="language-python highlighter-rouge"><div class="highlight"><pre class="highlight"><code>x = 1</code></pre></div></div>'
    out = enhance(html)
    assert_includes out, 'class="code-block" data-lang="python"'
    assert_includes out, '<span class="code-block__lang">Python</span>'
    assert_includes out, "data-copy hidden"
    assert_includes out, '<pre class="highlight" tabindex="0"><code>x = 1</code></pre>'
  end

  def test_lexerless_block_is_wrapped_too
    out = enhance('<pre><code class="language-promql">rate(x[5m])</code></pre>')
    assert_includes out, 'data-lang="promql"'
    assert_includes out, ">PromQL<"
  end

  def test_mermaid_becomes_diagram
    out = enhance('<pre><code class="language-mermaid">graph TD; A--&gt;B</code></pre>')
    assert_equal '<pre class="mermaid">graph TD; A--&gt;B</pre>', out
  end

  def test_headings_get_accessible_anchor
    out = enhance('<h2 id="setup">Set up <code>kubectl</code></h2>')
    assert_includes out, '<a class="heading-anchor" href="#setup" aria-label="Link to section: Set up kubectl"></a></h2>'
  end

  def test_tables_become_scrollable_regions
    assert_includes enhance("<table><tr><td>1</td></tr></table>"),
                    '<div class="table-wrap" role="region" aria-label="Table" tabindex="0"><table>'
  end

  def test_callout_syntaxes
    gfm = enhance("<blockquote>\n  <p>[!WARNING]\nDisk is full.</p>\n</blockquote>")
    assert_includes gfm, 'class="callout callout--warning"'
    assert_includes gfm, "Disk is full."
    refute_includes gfm, "[!WARNING]"

    bold = enhance("<blockquote>\n  <p><strong>Note</strong>: read this.</p>\n</blockquote>")
    assert_includes bold, 'class="callout callout--note"'

    chirpy = enhance(%(<blockquote class="prompt-tip">\n  <p>Use a cache.</p>\n</blockquote>))
    assert_includes chirpy, 'class="callout callout--tip"'
  end

  def test_plain_and_nested_blockquotes_are_preserved
    html = "<blockquote><p>Outer</p><blockquote><p>Inner</p></blockquote><p>After</p></blockquote><p>tail</p>"
    assert_equal html, enhance(html)
  end

  def test_images_are_lazy
    assert_includes enhance('<img src="a.png" alt="A">'), '<img loading="lazy" decoding="async" src="a.png"'
    assert_equal '<img loading="eager" src="a.png">', enhance('<img loading="eager" src="a.png">')
  end

  def test_summary_skips_headings_and_keeps_identifiers
    md = "## Introduction\n\nOur `grpc_request_duration_p99` metric dropped by **15%** across *several* services after the rollout."
    assert_equal "Our grpc_request_duration_p99 metric dropped by 15% across several services after the rollout.",
                 TechBlog::Content.summary(md)
  end

  def test_kind_heuristics
    assert_equal "Comparison", TechBlog::Content.kind_for("Helm vs Kustomize: A Comprehensive Comparison")
    assert_equal "Case Study", TechBlog::Content.kind_for("Fixing Event Loop Blocking in Python")
    assert_equal "Guide", TechBlog::Content.kind_for("Implementing Rate Limiting with Redis")
    assert_nil TechBlog::Content.kind_for("Python Metaclasses: What, Why, and How")
  end

  def test_toc_items_filter
    filter = Object.new.extend(TechBlog::ContentFilters)
    html = '<h2 id="a">Alpha &amp; Beta</h2><h3 id="b">Beta</h3><h4 id="c">skip</h4>'
    assert_equal [{ "id" => "a", "text" => "Alpha & Beta", "level" => 2 }, { "id" => "b", "text" => "Beta", "level" => 3 }],
                 filter.toc_items(html)
    assert_equal 1, filter.reading_minutes(10)
    assert_equal 3, filter.reading_minutes(600)
  end
end

class SiteBuildTest < Minitest::Test
  class << self
    def site_dir
      @site_dir ||= begin
        dir = Dir.mktmpdir("tech-blog-site")
        Minitest.after_run { FileUtils.remove_entry(dir) }
        config = Jekyll.configuration("source" => ROOT, "destination" => dir, "quiet" => true)
        Jekyll::Site.new(config).process
        dir
      end
    end
  end

  def read(path) = File.read(File.join(self.class.site_dir, path))
  def exist?(path) = File.exist?(File.join(self.class.site_dir, path))

  def test_repository_internals_are_not_published
    %w[pipeline server venv scripts .pipeline].each { |d| refute exist?(d), "#{d}/ must not be published" }
  end

  def test_filler_tags_do_not_exist_and_legacy_urls_redirect
    assert_includes read("tags/tech/index.html"), "url=/tabs/tags/" # retired filler tag -> tag index
    assert_includes read("tags/k8s/index.html"), "url=/tags/kubernetes/"
    assert_includes read("categories/tech/index.html"), "url=/tabs/categories/"
    assert_includes read("posts/2023-10-27-custom-grpc-load-balancer-teardown-a-contrarian-view/index.html"),
                    "url=/posts/custom-grpc-load-balancer-teardown-a-contrarian-view/"
  end

  def test_search_index_is_valid_and_complete
    entries = JSON.parse(read("assets/js/data/search.json"))
    posts = entries.select { |e| e["k"] == "post" }
    assert_operator posts.size, :>=, 60
    assert(entries.all? { |e| e["t"].is_a?(String) && !e["t"].empty? && e["u"].is_a?(String) })
    assert_equal 3, entries.count { |e| e["k"] == "course" }
  end

  def test_every_post_has_a_unique_meta_description
    pages = Dir[File.join(self.class.site_dir, "posts", "*", "index.html")].map { |f| File.read(f) }
    descriptions = pages.reject { |html| html.include?('http-equiv="refresh"') } # skip redirect stubs
                        .map { |html| html[/<meta name="description" content="([^"]*)"/, 1] }
    assert(descriptions.none? { |d| d.nil? || d.empty? }, "every post needs a meta description")
    assert_equal descriptions.size, descriptions.uniq.size, "meta descriptions must be unique"
  end

  def test_every_page_has_a_share_image
    missing = Dir[File.join(self.class.site_dir, "**", "index.html")].reject do |f|
      html = File.read(f)
      html.include?('http-equiv="refresh"') || html.include?('property="og:image"')
    end
    assert_empty missing, "pages without og:image"
  end

  def test_tag_counts_are_separated_from_names
    html = read("tabs/tags/index.html")
    assert_match(%r{kubernetes<span class="tag__count" aria-label="\d+ articles">\d+</span>}, html)
  end

  def test_course_pages_link_to_full_courses
    assert_includes read("courses/networking/index.html"), "https://course-computer-networks.riteshrana.engineer/"
    %w[computer-science computer-networks system-design].each do |c|
      assert_includes read("courses/index.html"), "https://course-#{c}.riteshrana.engineer/"
    end
  end
end
