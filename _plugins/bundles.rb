# frozen_string_literal: true

require "time"

# Article bundles: one folder per article.
#
#   content/posts/<slug>/index.md      -> /posts/<slug>/
#   content/posts/<slug>/diagram.webp  -> /posts/<slug>/diagram.webp
#
# Bundles are loaded into site.posts, so everything built on posts (home page,
# archive, categories/tags, feed, sitemap, search, related posts) discovers
# them with no further code. Legacy files in _posts/ keep working unchanged.
#
# Drafts: `draft: true` (bundle or _posts) keeps an article out of every
# production output. `jekyll serve --drafts` / `build --drafts` renders them.
#
# The content contract itself (required fields, slug rules, images) lives in
# content_contract.rb and is enforced by the test suite and CI.
module TechBlog
  module Bundles
    ROOT = "content/posts"
    # Must run before taxonomy normalization (:high = 30) and derived metadata
    # (:normal = 20) so bundles are in site.posts when those hooks run. Jekyll
    # only knows :low/:normal/:high by name; an integer sets an exact priority.
    HOOK_PRIORITY = 40

    # A file that sits next to an article's index.md, published under the
    # article's URL so relative references in Markdown resolve.
    class AssetFile < Jekyll::StaticFile
      def initialize(site, bundle_dir, slug, relative)
        super(site, site.source, File.join(ROOT, slug, File.dirname(relative)).chomp("/."), File.basename(relative))
        @asset_url = "/posts/#{slug}/#{relative}"
      end

      def url
        @asset_url
      end

      def destination(dest)
        @site.in_dest_dir(dest, Jekyll::URL.unescape_path(url))
      end
    end

    module_function

    def load(site)
      root = site.in_source_dir(ROOT)
      return unless File.directory?(root)

      Dir.children(root).sort.each do |slug|
        dir = File.join(root, slug)
        index = File.join(dir, "index.md")
        next unless File.file?(index)

        doc = Jekyll::Document.new(index, site: site, collection: site.posts)
        doc.data["slug"] = slug # URL comes from the folder name
        doc.read
        next unless publishable?(site, doc)

        # Jekyll adds a post's folder names ("content", "posts") as categories;
        # only the categories written in front matter are meaningful.
        doc.data["categories"] = front_matter_categories(index)

        doc.data["bundle"] = true
        apply_cover(doc, slug)
        doc.data["last_modified_at"] ||= doc.data["updated"] if doc.data["updated"]
        site.posts.docs << doc
        add_assets(site, dir, slug)
      end
      site.posts.docs.sort!
    end

    def front_matter_categories(index)
      data, = TechBlog::ContentContract.parse_front_matter(File.read(index))
      Array(data && data["categories"]).map(&:to_s)
    end

    def publishable?(site, doc)
      return false if doc.data["published"] == false
      return false if doc.data["draft"] == true && !site.show_drafts
      return false if doc.date > site.time && !site.future

      true
    end

    # cover: { image: cover.webp, alt: "..." }  ->  page.image for SEO/cards.
    def apply_cover(doc, slug)
      cover = doc.data["cover"]
      return unless cover.is_a?(Hash) && cover["image"].to_s != ""

      src = cover["image"].to_s
      src = "/posts/#{slug}/#{src.delete_prefix('./')}" unless src.start_with?("/", "http://", "https://")
      doc.data["image"] = { "path" => src, "alt" => cover["alt"].to_s }
      doc.data["cover_url"] = src
    end

    def add_assets(site, dir, slug)
      Dir.glob("**/*", base: dir).sort.each do |relative|
        next if relative == "index.md" || File.directory?(File.join(dir, relative))
        next if File.basename(relative).start_with?(".")

        site.static_files << AssetFile.new(site, dir, slug, relative)
      end
    end

    # Legacy _posts honour `draft: true` too.
    def drop_drafts(site)
      return if site.show_drafts

      site.posts.docs.reject! { |doc| doc.data["draft"] == true }
    end
  end
end

Jekyll::Hooks.register :site, :post_read, priority: TechBlog::Bundles::HOOK_PRIORITY do |site|
  TechBlog::Bundles.drop_drafts(site)
  TechBlog::Bundles.load(site)
end
