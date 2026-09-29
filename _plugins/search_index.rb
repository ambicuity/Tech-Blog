# frozen_string_literal: true

require "json"

# Emits /assets/js/data/search.json (the URL the previous theme used) for the
# client-side search dialog. Built from source Markdown during generation so it
# does not depend on render order. The dialog fetches it lazily on first open.
module TechBlog
  class SearchIndexGenerator < Jekyll::Generator
    safe true
    priority :low

    POST_BODY_CHARS = 2400
    PAGE_BODY_CHARS = 1200

    def generate(site)
      @titles = (site.data.dig("taxonomy", "categories") || []).to_h { |c| [c["name"], c["title"] || c["name"]] }
      entries = site.posts.docs.reject { |p| p.data["hidden"] }.reverse.map { |post| post_entry(post) }
      entries = course_entries(site) + entries
      entries += site.pages.filter_map { |page| page_entry(page) }

      index = Jekyll::PageWithoutAFile.new(site, site.source, "assets/js/data", "search.json")
      index.content = JSON.generate(entries)
      index.data.merge!("layout" => nil, "sitemap" => false)
      site.pages << index
    end

    private

    def course_entries(site)
      (site.data["course_sites"] || []).map do |c|
        {
          "t" => "#{c['title']} course", "u" => c["url"], "k" => "course", "c" => ["Courses"],
          "g" => Array(c["topics"]).map(&:downcase),
          "s" => "#{c['lessons']} lessons, #{c['phases']} phases. #{c['summary']}",
          "b" => c["description"].to_s
        }
      end
    end

    def post_entry(post)
      {
        "t" => post.data["title"].to_s,
        "u" => post.url,
        "d" => post.date.strftime("%Y-%m-%d"),
        "k" => "post",
        "c" => Array(post.data["categories"]).map { |c| @titles.fetch(c, c) },
        "g" => Array(post.data["tags"]),
        "s" => post.data["description"].to_s,
        "b" => plain_text(post.content, POST_BODY_CHARS)
      }
    end

    def page_entry(page)
      return nil unless page.ext == ".md"
      return nil if page.data["sitemap"] == false || page.data["title"].to_s.empty?

      course = page.data["course"]
      {
        "t" => page.data["title"].to_s,
        "u" => page.url,
        "k" => course ? "deep-dive" : "page",
        "c" => course ? [course["title"]] : [],
        "g" => [],
        "s" => page.data["description"].to_s,
        "b" => plain_text(page.content, PAGE_BODY_CHARS)
      }
    end

    # Markdown/Liquid/HTML -> searchable prose.
    def plain_text(markdown, limit)
      text = markdown.to_s
                     .gsub(/\{%.*?%\}|\{\{.*?\}\}/m, " ")
                     .gsub(/^\s*(```|~~~).*$/, " ")
                     .gsub(/<[^>]+>/, " ")
                     .gsub(/!\[[^\]]*\]\([^)]*\)/, " ")
                     .gsub(/\[([^\]]*)\]\([^)]*\)/, '\1')
                     .gsub(/[#>*_`|~]+/, " ")
                     .gsub(/\s+/, " ")
                     .strip
      text.length > limit ? "#{text[0, limit].sub(/\s\S*\z/, '')}…" : text
    end
  end
end
