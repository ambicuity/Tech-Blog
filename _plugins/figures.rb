# frozen_string_literal: true

# Figures: SVG diagrams inlined into the article at build time.
#
# In an article bundle, write
#
#   ![What the figure shows, for screen readers](outbox-flow.svg "Caption under the figure"){: .figure}
#
# and the SVG file next to index.md is inlined as <figure class="figure">. Inline
# (not <img>) so the figure uses the site's colors, fonts and light/dark theme
# through the classes in _sass/_figures.scss, and so assets/js/figures.js can
# step through its timeline (data-step / data-until). See docs/figures.md.
#
# Figures are authored by people and by automated authors, so the markup is
# sanitized here as well as rejected by the content contract: no scripts, styles,
# event handlers, foreignObject or external references. IDs are prefixed so two
# figures on one page cannot collide.
module TechBlog
  module Figures
    FIGURE_IMG = %r{<p>\s*(<img\b[^>]*\bclass="[^"]*\bfigure\b[^"]*"[^>]*>)\s*</p>}

    module_function

    def attribute(tag, name)
      tag[/\s#{name}="([^"]*)"/, 1]
    end

    def inline(html, dir, prefix)
      count = 0
      html.gsub(FIGURE_IMG) do
        original = Regexp.last_match(0)
        tag = Regexp.last_match(1)
        src = attribute(tag, "src").to_s.delete_prefix("./")
        path = File.join(dir, src)
        next original unless src.end_with?(".svg") && !src.include?("..") && File.file?(path)

        count += 1
        svg = sanitize(File.read(path), "#{prefix}-f#{count}").strip
        svg = accessible(svg, attribute(tag, "alt").to_s)
        caption = attribute(tag, "title")
        stepped = svg.include?("data-step") || svg.include?("data-until")
        %(<figure class="figure"#{' data-timeline' if stepped}>#{svg}) +
          (caption ? %(<figcaption>#{caption}</figcaption>) : "") + "</figure>"
      end
    end

    def sanitize(svg, prefix)
      svg = svg.sub(/\A\s*<\?xml[^>]*>/, "").gsub(/<!DOCTYPE[^>]*>/i, "").gsub(/<!--.*?-->/m, "")
      svg = svg.gsub(%r{<(script|style|foreignObject)\b.*?</\1\s*>}mi, "").gsub(%r{<(script|style|foreignObject)\b[^>]*/>}i, "")
      svg = svg.gsub(/\s+on[a-z]+\s*=\s*("[^"]*"|'[^']*')/i, "")
      svg = svg.gsub(/\s(?:xlink:)?href\s*=\s*("|')\s*(?!#)[^"']*\1/i, "") # only same-document references
      namespace_ids(svg, prefix).sub(/<svg\b([^>]*)>/) do
        attrs = Regexp.last_match(1).gsub(/\s(?:width|height|class)="[^"]*"/, "")
        %(<svg#{attrs} class="figure__svg" focusable="false">)
      end
    end

    def namespace_ids(svg, prefix)
      ids = svg.scan(/\sid="([^"]+)"/).flatten.uniq
      return svg if ids.empty?

      pattern = Regexp.union(ids.map { |id| /(?<![\w-])#{Regexp.escape(id)}(?![\w-])/ })
      svg.gsub(/(\sid="|url\(#|href="#|aria-(?:labelledby|describedby)=")([^"')]*)/) do
        lead, value = Regexp.last_match(1), Regexp.last_match(2)
        lead + value.gsub(pattern) { |id| "#{prefix}-#{id}" }
      end
    end

    # role="img" plus a name: the figure's own <title> if it has one, else the alt text.
    def accessible(svg, alt)
      svg.sub(/<svg\b([^>]*)>/) do
        attrs = Regexp.last_match(1)
        attrs += ' role="img"' unless attrs.include?("role=")
        attrs += %( aria-label="#{alt}") unless attrs.include?("aria-label") || attrs.include?("aria-labelledby") || alt.empty?
        "<svg#{attrs}>"
      end
    end
  end
end

Jekyll::Hooks.register :documents, :post_convert do |doc|
  next unless doc.data["bundle"] && doc.content.include?("figure")

  slug = File.basename(File.dirname(doc.path))
  doc.content = TechBlog::Figures.inline(doc.content, File.dirname(doc.path), slug.tr("^a-z0-9", "")[0, 12])
end
