# frozen_string_literal: true

require "cgi"
require "digest"
require "base64"

# Build-time enhancement of converted Markdown. Everything that can be decided
# statically happens here so the browser receives final markup: no layout
# shift, and the only client-side work is the copy button and scroll-spy.
#
#   * fenced code  -> labelled code block with a (JS-enabled) copy button
#   * h2-h4        -> linkable headings
#   * tables       -> keyboard-scrollable region
#   * blockquotes  -> callouts for [!NOTE] / **Note:** / Chirpy .prompt-* styles
#   * images       -> lazy + async decoding
#   * mermaid      -> <pre class="mermaid"> rendered on demand
module TechBlog
  module Content
    LANG_NAMES = {
      "bash" => "Shell", "sh" => "Shell", "shell" => "Shell", "zsh" => "Shell",
      "console" => "Terminal", "text" => "Output", "plaintext" => "Text",
      "python" => "Python", "py" => "Python", "yaml" => "YAML", "yml" => "YAML",
      "json" => "JSON", "dockerfile" => "Dockerfile", "docker" => "Dockerfile",
      "sql" => "SQL", "go" => "Go", "golang" => "Go", "java" => "Java",
      "javascript" => "JavaScript", "js" => "JavaScript", "typescript" => "TypeScript",
      "ts" => "TypeScript", "html" => "HTML", "xml" => "XML", "css" => "CSS",
      "c" => "C", "cpp" => "C++", "rust" => "Rust", "terraform" => "Terraform",
      "hcl" => "HCL", "toml" => "TOML", "ini" => "INI", "properties" => "Properties",
      "promql" => "PromQL", "protobuf" => "Protobuf", "proto" => "Protobuf",
      "diff" => "Diff", "gradle" => "Gradle", "groovy" => "Groovy",
      "assembly" => "Assembly", "nasm" => "Assembly", "make" => "Makefile",
      "nginx" => "Nginx", "ruby" => "Ruby", "php" => "PHP", "kotlin" => "Kotlin",
      "log" => "Log"
    }.freeze

    CALLOUTS = {
      "note" => "Note", "info" => "Note", "tip" => "Tip", "important" => "Important",
      "warning" => "Warning", "caution" => "Warning", "danger" => "Warning",
      "result" => "Result"
    }.freeze

    COPY_ICON = '<svg aria-hidden="true" viewBox="0 0 16 16" width="14" height="14">' \
                '<rect x="5.5" y="5.5" width="8" height="8" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.3"/>' \
                '<path d="M3.5 10.5h-.5A1 1 0 0 1 2 9.5V3a1 1 0 0 1 1-1h6.5a1 1 0 0 1 1 1v.5" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>'

    module_function

    def enhance(html)
      html = code_blocks(html)
      html = headings(html)
      html = tables(html)
      html = callouts(html)
      images(html)
    end

    def lang_label(lang)
      LANG_NAMES.fetch(lang.downcase) { lang.capitalize }
    end

    # Rouge-highlighted blocks, plus the bare <pre><code class="language-x">
    # kramdown emits when Rouge has no lexer for the language (promql, log, …).
    ROUGE_BLOCK = %r{<div class="(?:language-([\w+#.-]+) )?highlighter-rouge"><div class="highlight"><pre class="highlight"><code>(.*?)</code></pre></div>\s*</div>}m
    PLAIN_BLOCK = %r{<pre><code class="language-([\w+#.-]+)">(.*?)</code></pre>}m

    def code_blocks(html)
      html.gsub(ROUGE_BLOCK) { code_block(Regexp.last_match(1), Regexp.last_match(2)) }
          .gsub(PLAIN_BLOCK) { code_block(Regexp.last_match(1), Regexp.last_match(2)) }
    end

    def code_block(lang, code)
      return %(<pre class="mermaid">#{code}</pre>) if lang == "mermaid"

      label = lang ? lang_label(lang) : "Code"
      lang_attr = lang ? %( data-lang="#{CGI.escapeHTML(lang)}") : ""
      <<~HTML.strip
        <div class="code-block"#{lang_attr}><div class="code-block__bar"><span class="code-block__lang">#{label}</span><button type="button" class="code-block__copy" data-copy hidden>#{COPY_ICON}<span data-copy-label>Copy</span><span class="visually-hidden"> #{label} code</span></button></div><pre class="highlight" tabindex="0"><code>#{code}</code></pre></div>
      HTML
    end

    def headings(html)
      html.gsub(%r{<h([2-4]) id="([^"]+)">(.*?)</h\1>}m) do
        level, id, inner = Regexp.last_match.captures
        text = inner.gsub(/<[^>]+>/, "").strip
        %(<h#{level} id="#{id}">#{inner}<a class="heading-anchor" href="##{id}" aria-label="Link to section: #{CGI.escapeHTML(CGI.unescapeHTML(text))}"></a></h#{level}>)
      end
    end

    def tables(html)
      html.gsub(%r{<table>(.*?)</table>}m) do
        %(<div class="table-wrap" role="region" aria-label="Table" tabindex="0"><table>#{Regexp.last_match(1)}</table></div>)
      end
    end

    def images(html)
      html.gsub(/<img (?![^>]*\bloading=)/, '<img loading="lazy" decoding="async" ')
    end

    # Replace the blockquote that opens at +start+ (and ends at its matching
    # close tag) with a callout aside.
    def callouts(html)
      out = +""
      cursor = 0
      while (start = html.index("<blockquote", cursor))
        close = matching_close(html, start)
        break unless close

        block = html[start...close]
        replacement = callout_for(block)
        out << html[cursor...start] << (replacement || (block + "</blockquote>"))
        cursor = close + "</blockquote>".length
      end
      out << html[cursor..]
    end

    def matching_close(html, start)
      depth = 0
      pos = start
      while (m = html.match(%r{<(/?)blockquote\b[^>]*>}, pos))
        depth += m[1].empty? ? 1 : -1
        return m.begin(0) if depth.zero?

        pos = m.end(0)
      end
      nil
    end

    def callout_for(block)
      open_tag = block[/\A<blockquote[^>]*>/]
      body = block.delete_prefix(open_tag)
      kind = nil

      if (m = open_tag.match(/class="[^"]*prompt-(\w+)/))
        kind = m[1]
      elsif (m = body.match(/\A\s*<p>\[!(\w+)\]\s*/i))
        kind = m[1].downcase
        body = body.sub(m[0], "<p>")
      elsif (m = body.match(%r{\A\s*<p><strong>(Note|Tip|Important|Warning|Caution|Result)</strong>:?\s*}i))
        kind = m[1].downcase
        body = body.sub(m[0], "<p>")
      end
      return nil unless kind && CALLOUTS.key?(kind)

      label = CALLOUTS[kind]
      body = body.sub(%r{\A\s*<p>\s*</p>}, "")
      %(<aside class="callout callout--#{label.downcase}" aria-label="#{label}"><p class="callout__label">#{label}</p>#{body}</aside>)
    end

    # ---- derived post metadata ------------------------------------------

    KIND_RULES = [
      [/\bvs\.?\b|comparison/i, "Comparison"],
      [/contrarian|opinion|why .* (is|are) wrong/i, "Opinion"],
      [/deep dive|masterclass|explained|internals|\b101\b/i, "Deep Dive"],
      # Only a title that says so makes a Case Study: a problem-solving verb
      # ("Fixing ...") is not evidence that the event really happened.
      [/incident|case study|postmortem|post-mortem/i, "Case Study"],
      [/practical guide|guide|how to|from zero|tips|setting up|implementing|automating|^(fixing|debugging|mitigating|rejecting|refactoring)\b/i, "Guide"]
    ].freeze

    # `scenario: illustrative` articles narrate a composite, made-up situation;
    # they are always labelled Scenario, whatever the title suggests.
    def kind_for(title, scenario: nil)
      return "Scenario" if scenario == "illustrative"

      KIND_RULES.each { |re, kind| return kind if title.to_s.match?(re) }
      nil
    end

    SKIP_BLOCK = /\A(\#|```|~~~|>|\||<|---|\s*[-*+]\s|\s*\d+\.\s|\{%|!\[|\s{4})/.freeze

    # First real paragraph of a Markdown document, as plain text. Used for
    # cards and as the meta description when front matter has none.
    def summary(markdown, limit = 220)
      block = markdown.to_s.split(/\n\s*\n/).map(&:strip).find do |b|
        !b.empty? && !b.match?(SKIP_BLOCK) && b.length >= 60
      end
      return nil unless block

      text = block.gsub(/!\[[^\]]*\]\([^)]*\)/, "")
                  .gsub(/\[([^\]]+)\]\([^)]*\)/, '\\1')
                  .gsub(/<[^>]+>/, "")
                  .gsub(/(\*\*|__)(.+?)\1/, '\\2')
                  .gsub(/(?<![\w*])[*_](?![\s*_])(.+?)(?<![\s*_])[*_](?![\w*])/, '\\1')
                  .delete("`")
                  .gsub(/\s+/, " ").strip
      text.length > limit ? "#{text[0, limit].sub(/[\s,;:]+\S*\z/, '')}…" : text
    end

    def word_count(markdown)
      markdown.to_s.gsub(/```.*?```/m) { |code| code.split.first(code.split.size / 3).join(" ") }
              .scan(/[[:alnum:]’'-]+/).size
    end
  end

  # Liquid filters used by the layouts.
  module ContentFilters
    # [{ "id", "text", "level" }] for h2/h3 in rendered HTML.
    def toc_items(html)
      html.to_s.scan(%r{<h([23]) id="([^"]+)">(.*?)</h\1>}m).map do |level, id, inner|
        { "id" => id, "text" => CGI.unescapeHTML(inner.gsub(/<[^>]+>/, "").strip), "level" => level.to_i }
      end
    end

    # CSP source expression for an inline script body ('sha256-…').
    def csp_hash(input)
      "'sha256-#{Base64.strict_encode64(Digest::SHA256.digest(input.to_s))}'"
    end

    def reading_minutes(input)
      words = input.is_a?(Integer) ? input : TechBlog::Content.word_count(input)
      [(words / 230.0).ceil, 1].max
    end
  end
end

Liquid::Template.register_filter(TechBlog::ContentFilters)

markdown_doc = ->(doc) { %w(.md .markdown).include?(doc.extname.to_s.downcase) }

Jekyll::Hooks.register [:documents, :pages], :post_convert do |doc|
  doc.content = TechBlog::Content.enhance(doc.content) if markdown_doc.call(doc)
end

# Derived metadata: content kind, word count and related posts.
Jekyll::Hooks.register :site, :post_read do |site|
  posts = site.posts.docs.reject { |p| p.data["hidden"] }
  titles = (site.data.dig("taxonomy", "categories") || []).to_h { |c| [c["name"], c["title"] || c["name"]] }

  posts.each do |post|
    post.data["kind"] = "Scenario" if post.data["scenario"] == "illustrative"
    post.data["kind"] ||= TechBlog::Content.kind_for(post.data["title"])
    post.data["word_count"] = TechBlog::Content.word_count(post.content)
    post.data["summary"] = TechBlog::Content.summary(post.content)
    post.data["description"] ||= post.data["summary"]

    primary = Array(post.data["categories"]).first
    post.data["breadcrumbs"] = [
      { "title" => "Articles", "url" => "/tabs/archives/" },
      ({ "title" => titles.fetch(primary, primary), "url" => "/categories/#{Jekyll::Utils.slugify(primary)}/" } if primary),
      { "title" => post.data["title"] }
    ].compact
  end

  site.collections["tabs"]&.docs&.each do |tab|
    tab.data["breadcrumbs"] ||= [{ "title" => tab.data["title"] }]
  end

  posts.each do |post|
    tags = Array(post.data["tags"])
    primary = Array(post.data["categories"]).first
    scored = posts.filter_map do |other|
      next if other.equal?(post)

      score = (Array(other.data["tags"]) & tags).size
      score += 2 if Array(other.data["categories"]).first == primary
      [score, other] if score.positive?
    end
    post.data["related"] = scored.sort_by { |score, other| [-score, -other.date.to_i] }.first(3).map(&:last)
  end
end
