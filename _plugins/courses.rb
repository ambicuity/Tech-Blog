# frozen_string_literal: true

require "open3"
require "time"

# Deep Dives (the /courses/ tree) are plain Markdown pages. This hook gives
# them structure without touching the files:
#
#   * every page under courses/ renders with the `course` layout
#   * chapter order comes from the link order in the course's index.md, so the
#     syllabus stays the single source of truth for prev/next navigation
#   * pages whose Markdown starts with their own "# Heading" are flagged so the
#     layout does not print a second <h1>
#   * each course gets a last-updated date: the curated `updated` value in
#     _data/deep_dives.yml, else the date of the last git commit touching it
module TechBlog
  module Courses
    module_function

    def course_slug(page)
      page.relative_path[%r{\Acourses/([^/]+)/}, 1]
    end

    def git_updated(site, slug)
      out, status = Open3.capture2("git", "log", "-1", "--format=%cI", "--", "courses/#{slug}",
                                   chdir: site.source, err: File::NULL)
      status.success? && !out.strip.empty? ? Time.parse(out.strip) : nil
    rescue SystemCallError
      nil
    end

    def apply(site)
      pages = site.pages.select { |p| p.relative_path.start_with?("courses/") && p.ext == ".md" }
      by_slug = pages.group_by { |p| course_slug(p) }
      meta = (site.data["deep_dives"] || []).to_h { |d| [d["slug"], d] }

      by_slug.each do |slug, course_pages|
        index = course_pages.find { |p| p.name == "index.md" }
        chapters = order_chapters(slug, index, course_pages - [index])
        info = {
          "slug" => slug,
          "title" => meta.dig(slug, "title") || index&.data&.fetch("title", nil) || slug,
          "url" => "/courses/#{slug}/",
          "chapter_count" => chapters.size,
          # Curated date first: bulk formatting commits must not read as updates.
          "updated" => meta.dig(slug, "updated") || git_updated(site, slug)
        }

        course_pages.each do |page|
          page.data["layout"] = "course" if [nil, "page"].include?(page.data["layout"])
          page.data["course"] = info
          page.data["has_h1"] = page.content.to_s.lstrip.start_with?("# ")
          page.data["description"] ||= TechBlog::Content.summary(page.content)
          crumbs = [{ "title" => "Courses", "url" => "/courses/" }, { "title" => info["title"], "url" => info["url"] }]
          crumbs << { "title" => page.data["title"] } unless page == index
          crumbs.last.delete("url") if page == index
          page.data["breadcrumbs"] = crumbs
        end

        index&.data&.merge!("course_index" => true)
        chapters.each_with_index do |page, i|
          page.data["chapter_number"] = i + 1
          page.data["prev_chapter"] = link(chapters[i - 1]) if i.positive?
          page.data["next_chapter"] = link(chapters[i + 1]) if chapters[i + 1]
        end
      end

      site.data["courses"] = by_slug.transform_values { |ps| ps.first.data["course"] }
    end

    def link(page)
      { "title" => page.data["title"], "url" => page.url }
    end

    # Syllabus order first, then anything the syllabus does not link to
    # (natural sort on the numbers in the file name).
    def order_chapters(slug, index, chapters)
      linked = index ? index.content.scan(%r{\((/courses/#{Regexp.escape(slug)}/[^)#\s]+)\)}).flatten : []
      by_url = chapters.to_h { |p| [p.url, p] }
      ordered = linked.filter_map { |url| by_url.delete(url) || by_url.delete("#{url.chomp('/')}/") }
      rest = by_url.values.sort_by { |p| [p.name.scan(/\d+/).map(&:to_i), p.name] }
      ordered + rest
    end
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  TechBlog::Courses.apply(site)
end
