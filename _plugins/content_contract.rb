# frozen_string_literal: true

require "date"
require "time"
require "yaml"

# The article content contract, in one place. Used by:
#   * scripts/validate_content.rb  (CLI; CI runs it on every PR and deploy)
#   * scripts/publish_article.rb   (validates what it writes)
#   * test/plugins_test.rb
#
# Pure Ruby (no Jekyll needed). The human-readable version of these rules is
# docs/content-authoring.md — keep the two in sync.
module TechBlog
  module ContentContract
    SLUG_RE = /\A[a-z0-9]+(?:-[a-z0-9]+)*\z/
    MAX_SLUG = 80
    IMAGE_EXTS = %w[.webp .avif .png .jpg .jpeg .gif .svg].freeze
    MAX_IMAGE_BYTES = 5 * 1024 * 1024
    WARN_IMAGE_BYTES = 500 * 1024
    FRONT_MATTER_RE = /\A---\s*\n(.*?)\n---\s*\n/m
    # Legacy files in _posts/ written by the previous generator are only
    # checked for the essentials; stricter rules apply from this date.
    LEGACY_STRICT_FROM = "2026-01-01"
    # Placeholders a writer or generator left for itself, e.g. [CLAIM:ROOT_CAUSE],
    # [TODO], [INSERT diagram]. Checked outside code, in every article; link
    # text such as [INSERT statements](/posts/...) is not a marker.
    LEFTOVER_MARKER_RE = /\[(?:CLAIM|TODO|TBD|FIXME|INSERT|CITATION)(?:[:\s][^\]\n]*)?\](?!\()/
    # A line that is only a language name: a code block whose ``` fences were
    # stripped, which then renders (and is Liquid-processed) as prose.
    LOST_FENCE_RE = /^[ \t]*(?:yaml|bash|python|json|go|sh|shell|javascript|typescript|dockerfile|sql|hcl|terraform|console|promql|java|rust|toml)[ \t]*$/
    REFERENCES_HEADING_RE = /^##\s+(?:References|Sources|Further reading)\s*$/i

    Result = Struct.new(:path, :slug, :errors, :warnings) do
      def ok? = errors.empty?
    end

    module_function

    def taxonomy(root)
      @taxonomy ||= {}
      @taxonomy[root] ||= YAML.safe_load_file(File.join(root, "_data", "taxonomy.yml"))
    end

    def authors(root)
      @authors ||= {}
      @authors[root] ||= YAML.safe_load_file(File.join(root, "_data", "authors.yml")).keys
    end

    def slugify(text)
      text.to_s.downcase.gsub(/[^a-z0-9]+/, "-").gsub(/\A-+|-+\z/, "")
    end

    def parse_front_matter(source)
      match = source.match(FRONT_MATTER_RE)
      return [nil, source, "missing front matter block (--- ... ---) at the top of the file"] unless match

      data = YAML.safe_load(match[1], permitted_classes: [Date, Time], aliases: false)
      return [nil, source, "front matter must be a YAML mapping"] unless data.is_a?(Hash)

      [data, match.post_match, nil]
    rescue Psych::Exception => e
      [nil, source, "front matter is not valid YAML (quote values containing ': '): #{e.message.lines.first.strip}"]
    end

    def to_time(value)
      case value
      when Time then value
      when Date then value.to_time
      when String then Time.parse(value)
      end
    rescue ArgumentError
      nil
    end

    # Every article in the repository: [{ kind:, path:, slug: }]
    def discover(root)
      bundles = Dir.glob(File.join(root, "content", "posts", "*", "index.md")).sort.map do |path|
        { kind: :bundle, path: path, slug: File.basename(File.dirname(path)) }
      end
      legacy = Dir.glob(File.join(root, "_posts", "**", "*.md")).sort.map do |path|
        { kind: :legacy, path: path, slug: File.basename(path, ".md").sub(/\A\d{4}-\d{2}-\d{2}-/, "") }
      end
      bundles + legacy
    end

    def validate_all(root)
      entries = discover(root)
      results = entries.map { |e| e[:kind] == :bundle ? validate_bundle(root, e[:path]) : validate_legacy(root, e[:path]) }

      entries.group_by { |e| e[:slug] }.each do |slug, dupes|
        next if dupes.size < 2

        paths = dupes.map { |d| d[:path].delete_prefix("#{root}/") }
        results.each do |r|
          r.errors << "duplicate slug '#{slug}' (also used by #{(paths - [r.path]).join(', ')}): URLs would collide" if paths.include?(r.path)
        end
      end
      results
    end

    # Strict contract for content/posts/<slug>/index.md
    def validate_bundle(root, path)
      rel = path.delete_prefix("#{root}/")
      dir = File.dirname(path)
      slug = File.basename(dir)
      result = Result.new(rel, slug, [], [])
      errors = result.errors
      warnings = result.warnings

      errors << "folder name '#{slug}' is not a valid slug (lowercase letters, digits and single hyphens)" unless slug.match?(SLUG_RE)
      warnings << "slug is longer than #{MAX_SLUG} characters" if slug.length > MAX_SLUG

      data, body, error = parse_front_matter(File.read(path))
      if error
        errors << error
        return result
      end

      check_common(root, data, result)

      if data.key?("slug") && data["slug"].to_s != slug
        errors << "front matter slug '#{data['slug']}' does not match the folder name '#{slug}' (the folder name is the URL)"
      end

      description = data["description"].to_s.strip
      if description.empty?
        errors << "description is required"
      elsif description.length < 50 || description.length > 300
        warnings << "description is #{description.length} characters (aim for 120-200)"
      end

      if data["author"].to_s.empty?
        errors << "author is required (one of: #{authors(root).join(', ')})"
      end

      check_categories(root, data, result, strict: true)
      check_tags(data, result, required: true)
      check_cover(dir, data, result)
      check_body(dir, body, result)
      result
    end

    # Essentials for legacy _posts/YYYY-MM-DD-slug.md files.
    def validate_legacy(root, path)
      rel = path.delete_prefix("#{root}/")
      name = File.basename(path)
      result = Result.new(rel, name.sub(/\A\d{4}-\d{2}-\d{2}-/, "").delete_suffix(".md"), [], [])

      data, body, error = parse_front_matter(File.read(path))
      if error
        result.errors << error
        return result
      end

      check_common(root, data, result)
      check_markers(prose(body), result)
      check_categories(root, data, result, strict: false)
      result.errors << "tags are required" unless data.key?("tags")
      check_tags(data, result, required: false)

      file_date = name[0, 10]
      if file_date.match?(/\A\d{4}-\d{2}-\d{2}\z/) && file_date >= LEGACY_STRICT_FROM && (date = to_time(data["date"]))
        result.errors << "front-matter date #{date.strftime('%F')} does not match the file name date #{file_date}" if date.strftime("%F") != file_date
      end
      result
    end

    def check_common(root, data, result)
      title = data["title"]
      if !title.is_a?(String) || title.strip.empty?
        result.errors << "title is required"
      elsif title.length > 110
        result.warnings << "title is #{title.length} characters (search engines truncate around 60-70)"
      end

      if data["date"].nil?
        result.errors << "date is required (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS +0000)"
      elsif to_time(data["date"]).nil?
        result.errors << "date '#{data['date']}' is not a valid date"
      end

      if data.key?("updated")
        updated = to_time(data["updated"])
        published = to_time(data["date"])
        if updated.nil?
          result.errors << "updated '#{data['updated']}' is not a valid date"
        elsif published && updated < published
          result.errors << "updated (#{updated.strftime('%F')}) is earlier than date (#{published.strftime('%F')})"
        end
      end

      author = data["author"]
      if author && !authors(root).include?(author.to_s)
        result.errors << "unknown author '#{author}' (add it to _data/authors.yml or use: #{authors(root).join(', ')})"
      end

      %w[draft featured pin].each do |flag|
        result.errors << "#{flag} must be true or false" if data.key?(flag) && ![true, false].include?(data[flag])
      end

      if data.key?("canonical_url") && !data["canonical_url"].to_s.match?(%r{\Ahttps://\S+\z})
        result.errors << "canonical_url must be an absolute https:// URL"
      end
    end

    def check_categories(root, data, result, strict:)
      categories = data["categories"]
      if !categories.is_a?(Array) || categories.empty?
        result.errors << "categories must be a non-empty list (1-2 of: #{category_names(root).join(', ')})"
        return
      end

      result.warnings << "only the first two categories are used" if categories.size > 2
      return unless strict

      known = category_names(root).to_h { |n| [slugify(n), n] }
      aliases = taxonomy(root).fetch("category_aliases", {})
      categories.each do |cat|
        key = slugify(cat)
        next if known.key?(key)

        if aliases.key?(key) && aliases[key]
          result.warnings << "category '#{cat}' is an alias; use '#{aliases[key]}'"
        else
          result.errors << "unknown category '#{cat}' (use one of: #{category_names(root).join(', ')})"
        end
      end
    end

    def category_names(root)
      taxonomy(root).fetch("categories", []).map { |c| c["name"] }
    end

    def check_tags(data, result, required:)
      tags = data["tags"]
      if tags.nil?
        result.errors << "tags are required (3-8 lowercase, hyphenated tags)" if required
        return
      end
      unless tags.is_a?(Array) && tags.all? { |t| t.is_a?(String) || t.is_a?(Numeric) }
        result.errors << "tags must be a list of strings"
        return
      end

      result.errors << "tags must not be empty" if required && tags.empty?
      result.warnings << "#{tags.size} tags (aim for 3-8)" if required && !tags.empty? && (tags.size < 3 || tags.size > 8)
      messy = tags.map(&:to_s).reject { |t| t.match?(/\A[a-z0-9]+(?:[-.][a-z0-9]+)*\z/) }
      result.warnings << "tags are normalized at build time: #{messy.join(', ')}" if required && messy.any?
    end

    def check_cover(dir, data, result)
      cover = data["cover"]
      return if cover.nil?
      unless cover.is_a?(Hash)
        result.errors << "cover must be a mapping with image and alt"
        return
      end

      image = cover["image"].to_s
      result.errors << "cover.alt is required (describe the image for screen readers)" if cover["alt"].to_s.strip.empty?
      if image.empty?
        result.errors << "cover.image is required when cover is set"
      elsif !image.start_with?("http://", "https://", "/")
        check_local_image(dir, image, "cover.image", result)
      end
    end

    IMAGE_RE = /!\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)/
    HTML_IMG_RE = /<img\b[^>]*\bsrc=["']([^"']+)["'][^>]*>/i

    # Markdown without fenced code blocks or inline code spans.
    def prose(body)
      body.gsub(/^(```|~~~).*?^\1/m, "").gsub(/`[^`\n]*`/, "")
    end

    def check_markers(prose, result)
      lost = prose.scan(LOST_FENCE_RE).map(&:strip).uniq
      result.errors << "a code block lost its ``` fences (a line reads only '#{lost.join("', '")}'); wrap the code in ```lang ... ```" if lost.any?

      markers = prose.scan(LEFTOVER_MARKER_RE).uniq
      return if markers.empty?

      result.errors << "leftover placeholder(s) in the text: #{markers.join(', ')} (remove them or write the missing content)"
    end

    def check_sources(prose, result)
      result.warnings << "no links to other articles (aim for 2-4, e.g. [title](/posts/<slug>/))" unless prose.include?("](/posts/")

      heading = prose.match(REFERENCES_HEADING_RE)
      unless heading
        result.warnings << "no ## References section (list the primary sources that support the article)"
        return
      end

      section = heading.post_match.split(/^##\s/, 2).first
      linked = section.gsub(/\[[^\]]*\]\([^)]*\)/, "").gsub(%r{<https?://[^>]+>}, "")
      bare = linked.scan(%r{https?://[^\s)>\]]+}).size
      return if bare.zero?

      result.warnings << "References: #{bare} bare URL(s) render as plain, unclickable text; write [Title](https://...)"
    end

    def check_body(dir, body, result)
      prose = prose(body)
      check_markers(prose, result)
      check_sources(prose, result)
      result.warnings << "body contains a level-1 heading; the title already renders as <h1> (start sections at ##)" if prose.match?(/^#\s/)

      prose.scan(IMAGE_RE).each do |alt, src|
        result.warnings << "image '#{src}' has no alt text" if alt.strip.empty?
        next if src.start_with?("http://", "https://", "/", "data:")

        check_local_image(dir, src, "image", result)
      end
      prose.scan(HTML_IMG_RE).each do |(src)|
        next if src.start_with?("http://", "https://", "/", "data:")

        check_local_image(dir, src, "image", result)
      end
    end

    def check_local_image(dir, src, label, result)
      relative = src.delete_prefix("./")
      if relative.include?("..")
        result.errors << "#{label} '#{src}' must stay inside the article folder"
        return
      end
      file = File.join(dir, relative)
      unless File.file?(file)
        result.errors << "#{label} '#{src}' not found in the article folder"
        return
      end
      unless IMAGE_EXTS.include?(File.extname(file).downcase)
        result.errors << "#{label} '#{src}' has an unsupported type (use #{IMAGE_EXTS.join(', ')})"
        return
      end

      size = File.size(file)
      if size > MAX_IMAGE_BYTES
        result.errors << "#{label} '#{src}' is #{size / 1024} KiB (limit #{MAX_IMAGE_BYTES / 1024 / 1024} MiB)"
      elsif size > WARN_IMAGE_BYTES
        result.warnings << "#{label} '#{src}' is #{size / 1024} KiB; compress it (WebP, under 500 KiB)"
      end
    end
  end
end
