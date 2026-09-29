# frozen_string_literal: true

require "net/http"
require "open3"
require "openssl"
require "uri"

# External-reference checking for articles (scripts/check_external_links.rb).
#
# A reference that returns 404/410, or a host that does not exist, is broken.
# Anything else that is not a success (403 from bot protection, 429, 5xx,
# timeouts, TLS trouble) is "unverified": reported, but not proof the page is
# gone, so it never fails a pull request on its own.
module TechBlog
  module ExternalLinks
    Check = Struct.new(:url, :verdict, :detail)

    MAX_REDIRECTS = 5
    BROKEN_STATUSES = [404, 410].freeze
    # HEAD is refused or mishandled by some servers; retry those with GET.
    RETRY_WITH_GET = [400, 403, 405, 501].freeze
    USER_AGENT = "Mozilla/5.0 (compatible; tech-blog-link-check; +https://blog.riteshrana.engineer)"
    # Hosts used in examples, never real references.
    PLACEHOLDER_HOST_RE = /\A(?:localhost|127\.\d+\.\d+\.\d+|0\.0\.0\.0|\[::1\]|(?:.+\.)?example\.(?:com|org|net)|.+\.(?:example|local|internal|localhost|test|invalid))\z/i
    # IP literals (10.0.0.12, 10.x.x.x) only appear in examples.
    IP_LITERAL_RE = /\A[\dx]{1,3}(?:\.[\dx]{1,3}){3}\z/i
    UNREACHABLE = [SocketError, Errno::ECONNREFUSED, Errno::EHOSTUNREACH, Errno::ENETUNREACH].freeze

    module_function

    # Unique http(s) URLs in Markdown prose (fenced code and inline code are
    # examples, not references), in order of first appearance.
    def extract(markdown)
      prose = markdown.gsub(/^(```|~~~).*?^\1/m, "").gsub(/`[^`\n]*`/, "")
      prose.scan(%r{https?://[^\s<>()\[\]"'`]+(?:\([^\s()]*\)[^\s<>()\[\]"'`]*)*})
           .map { |url| url.sub(/[.,;:!?*_]+\z/, "") }
           .uniq
    end

    def checkable?(url)
      host = URI.parse(url).host
      !host.nil? && host.include?(".") && !host.match?(PLACEHOLDER_HOST_RE) && !host.match?(IP_LITERAL_RE)
    rescue URI::InvalidURIError
      false
    end

    def check(url, timeout: 15)
      uri = URI.parse(url)
      method = :head
      MAX_REDIRECTS.times do
        response = request(uri, method, timeout)
        code = response.code.to_i
        if response.is_a?(Net::HTTPRedirection) && response["location"]
          uri = URI.join(uri.to_s, response["location"])
          next
        end
        return Check.new(url, :ok, code.to_s) if response.is_a?(Net::HTTPSuccess)
        if method == :head && RETRY_WITH_GET.include?(code)
          method = :get
          redo
        end
        return Check.new(url, :broken, "HTTP #{code}") if BROKEN_STATUSES.include?(code)

        return Check.new(url, :unverified, "HTTP #{code}")
      end
      Check.new(url, :unverified, "more than #{MAX_REDIRECTS} redirects")
    rescue *UNREACHABLE => e
      Check.new(url, :broken, "unreachable (#{e.class.name.split('::').last}: #{e.message.lines.first&.strip})")
    rescue URI::InvalidURIError, ArgumentError => e
      Check.new(url, :broken, "invalid URL (#{e.message})")
    rescue Net::OpenTimeout, Net::ReadTimeout, OpenSSL::SSL::SSLError, IOError, SystemCallError => e
      Check.new(url, :unverified, "#{e.class.name.split('::').last}: #{e.message.lines.first&.strip}")
    end

    def request(uri, method, timeout)
      Net::HTTP.start(uri.host, uri.port, use_ssl: uri.scheme == "https",
                                          open_timeout: timeout, read_timeout: timeout) do |http|
        klass = method == :head ? Net::HTTP::Head : Net::HTTP::Get
        req = klass.new(uri.request_uri, "User-Agent" => USER_AGENT, "Accept" => "*/*")
        # For GET, stop after the headers: only the status matters.
        http.request(req) { |res| return res }
      end
    end

    # Article files (index.md or _posts/*.md) touched between base and HEAD.
    def changed_articles(root, base)
      out, status = Open3.capture2("git", "-C", root, "diff", "--name-only", "--diff-filter=ACMR", "#{base}...HEAD")
      raise "git diff against #{base} failed" unless status.success?

      out.lines(chomp: true).filter_map do |path|
        if (m = path.match(%r{\Acontent/posts/([^/]+)/}))
          "content/posts/#{m[1]}/index.md"
        elsif path.match?(%r{\A_posts/.+\.md\z})
          path
        end
      end.uniq.select { |path| File.file?(File.join(root, path)) }
    end
  end
end
