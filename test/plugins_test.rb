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
require "base64"
require "fileutils"
require "open3"
require "rbconfig"
require "socket"

ROOT = File.expand_path("..", __dir__)
Dir[File.join(ROOT, "_plugins", "*.rb")].sort.each { |f| require f }
require_relative "../scripts/support/external_links"

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

# Pre-deploy guard: every article in the repository satisfies the content
# contract (_plugins/content_contract.rb, docs/content-authoring.md). A failure
# here fails CI and the deploy, so a malformed article can never go live.
class RepositoryContentTest < Minitest::Test
  RESULTS = TechBlog::ContentContract.validate_all(ROOT)

  RESULTS.each do |result|
    define_method("test_contract_#{result.path.tr('^a-zA-Z0-9', '_')}") do
      assert result.ok?, "#{result.path}:\n  #{result.errors.join("\n  ")}"
    end
  end
end

# Contract rules, exercised against throwaway repositories.
class ContentContractTest < Minitest::Test
  GOOD = {
    "title" => "Retry-safe consumers",
    "description" => "How to make message consumers safe to retry with idempotency keys and a single transaction.",
    "date" => "2026-09-01 10:00:00 +0000",
    "author" => "ritesh",
    "categories" => ["Distributed Systems"],
    "tags" => %w[idempotency kafka reliability]
  }.freeze

  def setup
    @root = Dir.mktmpdir("contract")
    FileUtils.mkdir_p(File.join(@root, "_data"))
    %w[taxonomy.yml authors.yml].each { |f| FileUtils.cp(File.join(ROOT, "_data", f), File.join(@root, "_data")) }
  end

  def teardown = FileUtils.remove_entry(@root)

  def bundle(slug, front = GOOD, body: "Intro paragraph.\n\n## Section\n\nText.", files: {})
    dir = File.join(@root, "content", "posts", slug)
    FileUtils.mkdir_p(dir)
    File.write(File.join(dir, "index.md"), "#{YAML.dump(front)}---\n\n#{body}\n")
    files.each { |name, bytes| File.binwrite(File.join(dir, name), bytes) }
    TechBlog::ContentContract.validate_bundle(@root, File.join(dir, "index.md"))
  end

  def test_valid_bundle_passes
    result = bundle("retry-safe-consumers")
    assert result.ok?, result.errors.inspect
  end

  def test_required_fields
    %w[title description date author categories tags].each do |key|
      result = bundle("missing-#{key}", GOOD.reject { |k, _| k == key })
      refute result.ok?, "missing #{key} should fail"
    end
  end

  def test_slug_rules
    refute bundle("Bad_Slug").ok?
    refute bundle("good-slug", GOOD.merge("slug" => "other-slug")).ok?, "front matter slug must match folder"
  end

  def test_invalid_dates
    refute bundle("bad-date", GOOD.merge("date" => "yesterday-ish")).ok?
    refute bundle("updated-before", GOOD.merge("updated" => "2025-01-01")).ok?
  end

  def test_unknown_category_and_author
    refute bundle("unknown-cat", GOOD.merge("categories" => ["Astrology"])).ok?
    refute bundle("unknown-author", GOOD.merge("author" => "Senior Staff Engineer")).ok?
  end

  def test_draft_must_be_boolean
    assert bundle("draft-ok", GOOD.merge("draft" => true)).ok?
    refute bundle("draft-bad", GOOD.merge("draft" => "yes")).ok?
  end

  def test_images_must_exist_and_cover_needs_alt
    refute bundle("missing-image", body: "![Diagram](diagram.webp)").ok?
    assert bundle("present-image", body: "![Diagram](diagram.webp)", files: { "diagram.webp" => "x" }).ok?
    refute bundle("escape-folder", body: "![Diagram](../other/diagram.webp)").ok?
    refute bundle("cover-no-alt", GOOD.merge("cover" => { "image" => "cover.webp" }), files: { "cover.webp" => "x" }).ok?
    assert bundle("cover-ok", GOOD.merge("cover" => { "image" => "cover.webp", "alt" => "A diagram" }),
                  files: { "cover.webp" => "x" }).ok?
  end

  def test_invalid_yaml_is_an_error
    dir = File.join(@root, "content", "posts", "broken-yaml")
    FileUtils.mkdir_p(dir)
    File.write(File.join(dir, "index.md"), "---\ntitle: Kafka: Why Consumers Stall\n---\nBody\n")
    result = TechBlog::ContentContract.validate_bundle(@root, File.join(dir, "index.md"))
    assert_match(/not valid YAML/, result.errors.join)
  end

  def test_duplicate_slugs_across_bundles_and_posts
    bundle("same-slug")
    FileUtils.mkdir_p(File.join(@root, "_posts"))
    File.write(File.join(@root, "_posts", "2026-01-05-same-slug.md"), "#{YAML.dump(GOOD)}---\nBody\n")
    dupes = TechBlog::ContentContract.validate_all(@root).reject(&:ok?)
    assert_equal 2, dupes.size
    assert(dupes.all? { |r| r.errors.join.include?("duplicate slug") })
  end

  def test_leftover_generator_markers_fail
    %w[[CLAIM:ROOT_CAUSE] [TODO] [TODO:\ add\ numbers] [INSERT\ diagram] [TBD] [FIXME]].each_with_index do |marker, i|
      result = bundle("marker-#{i}", body: "The cause was a bad rule #{marker}.\n\n## Section\n\nText.")
      assert_match(/leftover placeholder/, result.errors.join, marker)
    end
  end

  def test_markers_in_code_and_ordinary_brackets_are_fine
    body = "Use `[TODO]` in comments.\n\n```python\n# [CLAIM:X] is fine in code\n```\n\n" \
           "> [!NOTE]\n> A callout.\n\nSee the [TODO list](/posts/x/) and [INSERT statements](/posts/y/)."
    assert bundle("markers-ok", body: body).ok?
  end

  def test_leftover_markers_fail_in_legacy_posts_too
    FileUtils.mkdir_p(File.join(@root, "_posts"))
    path = File.join(@root, "_posts", "2024-07-30-old-post.md")
    File.write(path, "#{YAML.dump(GOOD)}---\nA partial outage [CLAIM:FAILURE_MODE].\n")
    assert_match(/leftover placeholder/, TechBlog::ContentContract.validate_legacy(@root, path).errors.join)
  end

  def test_code_block_that_lost_its_fences_fails
    result = bundle("lost-fence", body: "Apply it:\n\nyaml\napiVersion: v1\nkind: Service\n\n\nDone.")
    assert_match(/lost its ``` fences/, result.errors.join)
    in_list = bundle("lost-fence-list", body: "*   Drain the node:\n\n    bash\n    kubectl drain node-1\n    \n")
    assert_match(/lost its ``` fences/, in_list.errors.join)
    assert bundle("kept-fence", body: "Apply it:\n\n```yaml\napiVersion: v1\n```\n\nWe use yaml\nfor config.").ok?
  end

  def test_references_and_internal_links_are_encouraged
    bare = bundle("bare-refs", body: "Text.\n\n## References\n\n- Pattern docs — https://example.org/pattern\n")
    assert bare.ok?, "reference style is a warning, not an error"
    assert_match(/bare URL/, bare.warnings.join)
    assert_match(/no links to other articles/, bare.warnings.join)

    missing = bundle("no-refs", body: "Text with [a link](/posts/other/).\n\n## Section\n\nMore.")
    assert_match(/References section/, missing.warnings.join)

    good = bundle("good-refs", body: "See [related](/posts/other/).\n\n## References\n\n" \
                                     "- [Pattern docs](https://example.org/pattern)\n- <https://example.org/spec>\n")
    assert_empty good.warnings.grep(/References|bare URL|other articles/)
  end
end

# scripts/support/external_links.rb: the external-reference check for changed articles.
class ExternalLinksTest < Minitest::Test
  Links = TechBlog::ExternalLinks

  # A tiny HTTP server so the checker is tested without the internet.
  def setup
    @server = TCPServer.new("127.0.0.1", 0)
    @base = "http://127.0.0.1:#{@server.addr[1]}"
    @thread = Thread.new { loop { serve(@server.accept) } }
  end

  def teardown
    @thread.kill
    @server.close
  end

  def serve(client)
    method, path = client.gets.to_s.split
    nil until client.gets.to_s.strip.empty?
    status, headers = case path
                      when "/ok" then ["200 OK", {}]
                      when "/moved" then ["301 Moved Permanently", { "Location" => "/ok" }]
                      when "/moved-to-gone" then ["302 Found", { "Location" => "#{@base}/gone" }]
                      when "/gone" then ["404 Not Found", {}]
                      when "/no-head" then method == "HEAD" ? ["405 Method Not Allowed", {}] : ["200 OK", {}]
                      when "/blocked" then ["403 Forbidden", {}]
                      when "/busy" then ["503 Service Unavailable", {}]
                      else ["404 Not Found", {}]
                      end
    head = headers.merge("Content-Length" => "0", "Connection" => "close").map { |k, v| "#{k}: #{v}\r\n" }.join
    client.write("HTTP/1.1 #{status}\r\n#{head}\r\n")
  ensure
    client&.close
  end

  def verdict(path) = Links.check("#{@base}#{path}", timeout: 3).verdict

  def test_classifies_responses
    assert_equal :ok, verdict("/ok")
    assert_equal :ok, verdict("/moved")
    assert_equal :ok, verdict("/no-head"), "falls back to GET when HEAD is refused"
    assert_equal :broken, verdict("/gone")
    assert_equal :broken, verdict("/moved-to-gone")
    assert_equal :unverified, verdict("/blocked"), "bot-blocking is not proof the page is gone"
    assert_equal :unverified, verdict("/busy")
  end

  def test_unreachable_host_is_broken
    port = TCPServer.open("127.0.0.1", 0) { |s| s.addr[1] } # closed port
    assert_equal :broken, Links.check("http://127.0.0.1:#{port}/", timeout: 3).verdict
  end

  def test_extracts_links_outside_code
    markdown = <<~MD
      Read [the pattern](https://microservices.io/patterns/data/transactional-outbox.html) and
      <https://kafka.apache.org/documentation/>. Also https://debezium.io/documentation/.
      Local [post](/posts/other/) and [section](#refs) are not external.

      ```bash
      curl https://api.example.net/in-code
      ```

      Run `curl https://inline.example.net/x` too. [Same](https://kafka.apache.org/documentation/)
    MD
    assert_equal %w[
      https://microservices.io/patterns/data/transactional-outbox.html
      https://kafka.apache.org/documentation/
      https://debezium.io/documentation/
    ], Links.extract(markdown)
  end

  def test_skips_placeholder_and_local_hosts
    %w[http://localhost:8080/x http://127.0.0.1/ https://example.com/a https://api.example.org
       http://my-svc.default.svc.cluster.local/ http://host.internal/ http://10.x.x.x:8080/health
       http://10.0.0.12/].each do |url|
      refute Links.checkable?(url), url
    end
    assert Links.checkable?("https://kafka.apache.org/documentation/")
  end
end

# scripts/publish_article.rb: JSON package -> validated bundle, or nothing.
class PublishArticleTest < Minitest::Test
  SCRIPT = File.join(ROOT, "scripts", "publish_article.rb")

  def setup
    @root = Dir.mktmpdir("publish")
    %w[_data _posts].each { |d| FileUtils.cp_r(File.join(ROOT, d), @root) }
  end

  def teardown = FileUtils.remove_entry(@root)

  def publish(package, *flags)
    path = File.join(@root, "package.json")
    File.write(path, JSON.generate(package))
    out, status = Open3.capture2e({ "BLOG_ROOT" => @root }, RbConfig.ruby, SCRIPT, path, "--json", *flags)
    [JSON.parse(out), status]
  end

  def package
    {
      "title" => "Kafka Rebalances: Why Consumers Stall",
      "description" => "What happens to in-flight messages during a consumer-group rebalance, and how to keep processing safe.",
      "date" => "2026-09-02",
      "categories" => ["Distributed Systems"],
      "tags" => %w[kafka reliability consumers],
      "content" => "Rebalances pause consumption.\n\n## Why\n\n![Timeline](timeline.png)",
      "images" => [{ "name" => "timeline.png", "base64" => Base64.strict_encode64("fake-png") }]
    }
  end

  def test_creates_valid_bundle_with_safe_front_matter
    result, status = publish(package)
    assert status.success?, result.inspect
    index = File.join(@root, "content", "posts", "kafka-rebalances-why-consumers-stall", "index.md")
    assert File.exist?(index)
    assert File.exist?(File.join(File.dirname(index), "timeline.png"))
    data, = TechBlog::ContentContract.parse_front_matter(File.read(index))
    assert_equal "Kafka Rebalances: Why Consumers Stall", data["title"], "colon in the title must survive as valid YAML"
    assert_equal false, data["draft"]
  end

  def test_rejects_invalid_package_and_writes_nothing
    result, status = publish(package.merge("categories" => ["Astrology"]))
    refute status.success?
    refute result["ok"]
    refute Dir.exist?(File.join(@root, "content", "posts", "kafka-rebalances-why-consumers-stall"))
  end

  def test_refuses_to_overwrite_without_force
    publish(package)
    result, status = publish(package)
    refute status.success?
    assert_match(/already exists/, result["errors"].join)
    _, forced = publish(package, "--force")
    assert forced.success?
  end

  def test_dry_run_writes_nothing
    result, status = publish(package, "--dry-run")
    assert status.success?
    assert result["dry_run"]
    refute Dir.exist?(File.join(@root, "content", "posts", "kafka-rebalances-why-consumers-stall"))
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

  def self.draft_bundles
    Dir[File.join(ROOT, "content", "posts", "*", "index.md")].filter_map do |index|
      data, = TechBlog::ContentContract.parse_front_matter(File.read(index))
      File.basename(File.dirname(index)) if data && data["draft"] == true
    end
  end

  def test_drafts_never_reach_production_outputs
    drafts = self.class.draft_bundles
    skip "no draft bundles in the repository" if drafts.empty?
    feed, sitemap, search = read("feed.xml"), read("sitemap.xml"), read("assets/js/data/search.json")
    drafts.each do |slug|
      refute exist?("posts/#{slug}/index.html"), "draft #{slug} was rendered"
      refute Dir.exist?(File.join(self.class.site_dir, "posts", slug)), "draft #{slug} assets were published"
      [feed, sitemap, search].each { |out| refute_includes out, "/posts/#{slug}/" }
    end
    refute exist?("content"), "bundles must not also render as plain pages under /content/"
  end

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

# `jekyll build --drafts`: draft bundles render completely, so authors (and
# Muse) can preview an article before switching it to published.
class DraftPreviewBuildTest < Minitest::Test
  def self.site_dir
    @site_dir ||= begin
      dir = Dir.mktmpdir("tech-blog-drafts")
      Minitest.after_run { FileUtils.remove_entry(dir) }
      config = Jekyll.configuration("source" => ROOT, "destination" => dir, "quiet" => true, "show_drafts" => true)
      Jekyll::Site.new(config).process
      dir
    end
  end

  def test_draft_bundles_render_with_assets_and_listings
    drafts = SiteBuildTest.draft_bundles
    skip "no draft bundles in the repository" if drafts.empty?
    drafts.each do |slug|
      page = File.join(self.class.site_dir, "posts", slug, "index.html")
      assert File.exist?(page), "draft #{slug} did not render with --drafts"
      html = File.read(page)
      assert_includes html, 'class="article-head__title"'
      assert_includes html, "data-toc-link"

      bundle_dir = File.join(ROOT, "content", "posts", slug)
      Dir.glob("**/*", base: bundle_dir).each do |asset|
        next if asset == "index.md" || File.directory?(File.join(bundle_dir, asset))

        assert File.exist?(File.join(self.class.site_dir, "posts", slug, asset)), "asset #{asset} not published"
      end
      assert_includes File.read(File.join(self.class.site_dir, "feed.xml")), "/posts/#{slug}/"
    end
  end

  def test_bundle_categories_come_from_front_matter_only
    refute Dir.exist?(File.join(self.class.site_dir, "categories", "content")), "folder names leaked into categories"
    refute Dir.exist?(File.join(self.class.site_dir, "categories", "posts"))
  end
end
