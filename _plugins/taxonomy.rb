# frozen_string_literal: true

require "set"

# Normalizes post tags and categories against _data/taxonomy.yml and emits
# redirect pages for taxonomy URLs that were retired during the cleanup.
#
# Runs on :post_read so that site.tags / site.categories and jekyll-archives
# (a generator) only ever see canonical names.

module TechBlog
  module Taxonomy
    module_function

    def normalize_tag(raw, aliases, drop)
      tag = raw.to_s.strip.downcase
      return nil if tag.empty?

      tag = tag.gsub(/[^a-z0-9.\-]+/, "-").squeeze("-").delete_prefix("-").delete_suffix("-")
      return nil if tag.empty? # e.g. a tag made only of symbols or emoji

      tag = aliases.fetch(tag, tag)
      drop.include?(tag) ? nil : tag
    end

    def normalize_categories(raw, config)
      canonical = config.fetch("categories", []).map { |c| c["name"] }
      by_slug = canonical.to_h { |name| [Jekyll::Utils.slugify(name), name] }
      aliases = config.fetch("category_aliases", {})

      names = Array(raw).map do |cat|
        slug = Jekyll::Utils.slugify(cat.to_s)
        next by_slug[slug] if by_slug.key?(slug)
        next aliases[slug] if aliases.key?(slug) # may be nil => removed

        Jekyll.logger.warn "Taxonomy:", "unknown category '#{cat}' (add it to _data/taxonomy.yml)"
        nil
      end

      names = names.compact.uniq.first(2)
      names.empty? ? [config.fetch("default_category")] : names
    end

    def apply(site)
      config = site.data["taxonomy"] || {}
      aliases = config.fetch("tag_aliases", {}).transform_keys(&:to_s)
      drop = config.fetch("tag_drop", []).map(&:to_s)

      authors = site.data["authors"] || {}
      site.posts.docs.each do |post|
        author = post.data["author"]
        unless author.nil? || authors.key?(author.to_s)
          Jekyll.logger.warn "Taxonomy:", "unknown author '#{author}' in #{post.relative_path}; using site author"
          post.data["author"] = authors.keys.first
        end

        tags = Array(post.data["tags"]).map { |t| normalize_tag(t, aliases, drop) }.compact.uniq
        post.data["tags"] = tags
        post.data["categories"] = normalize_categories(post.data["categories"], config)
      end
    end
  end

  # A minimal page that sends visitors (and crawlers) from a retired URL to its
  # canonical replacement.
  class RedirectPage < Jekyll::PageWithoutAFile
    def initialize(site, from, to)
      super(site, site.source, from, "index.html")
      self.content = ""
      data.merge!(
        "layout" => "redirect",
        "redirect_to" => to,
        "sitemap" => false,
        "title" => "Redirecting…"
      )
    end
  end

  class LegacyRedirectGenerator < Jekyll::Generator
    safe true
    priority :lowest

    def generate(site)
      # jekyll-archives pages bypass front-matter defaults; give them the
      # default share image too (runs last, after jekyll-archives).
      share_image = site.config.dig("social", "image")
      site.pages.each { |page| page.data["image"] ||= share_image } if share_image

      legacy = site.data["legacy_redirects"] || {}
      taken = site.pages.map(&:url).to_set

      redirects = (legacy["paths"] || {}).dup
      { "tags" => "tags", "categories" => "categories" }.each do |key, prefix|
        (legacy[key] || {}).each { |slug, target| redirects["/#{prefix}/#{slug}/"] = target }
      end

      redirects.each do |from, target|
        next if taken.include?(from) # a live page exists again; never shadow it

        site.pages << RedirectPage.new(site, from, target)
      end
    end
  end
end

# High priority: related posts, search and archives must see canonical names.
Jekyll::Hooks.register :site, :post_read, priority: :high do |site|
  TechBlog::Taxonomy.apply(site)
end
