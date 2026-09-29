#!/usr/bin/env ruby
# frozen_string_literal: true

# Check the external links (references) in articles.
#
#   ruby scripts/check_external_links.rb content/posts/my-article      # one article
#   ruby scripts/check_external_links.rb --changed-since origin/main   # articles changed on this branch
#   ruby scripts/check_external_links.rb --json ...                    # machine-readable output
#
# With no paths and no --changed-since, every bundle in content/posts/ is checked.
# Links inside code blocks and to example hosts (localhost, example.com, ...)
# are skipped.
#
# Exit status: 1 if any link is broken (HTTP 404/410 or the host does not
# exist); links that could not be verified (403, 429, 5xx, timeouts) are
# reported as warnings only.

require "json"
require_relative "support/external_links"

Links = TechBlog::ExternalLinks
ROOT = ENV.fetch("BLOG_ROOT", File.expand_path("..", __dir__))
THREADS = 8

args = ARGV.dup
json = args.delete("--json")
base = (i = args.index("--changed-since")) && args.slice!(i, 2)[1]
abort "usage: ruby scripts/check_external_links.rb [--changed-since REF] [--json] [article ...]" if args.any? { |a| a.start_with?("--") }

articles =
  if base
    Links.changed_articles(ROOT, base)
  elsif args.any?
    args.map do |arg|
      path = File.expand_path(arg)
      path = File.join(path, "index.md") if File.directory?(path)
      abort "not an article: #{arg}" unless File.file?(path)
      path.delete_prefix("#{ROOT}/")
    end
  else
    Dir.glob("content/posts/*/index.md", base: ROOT).sort
  end

urls_by_article = articles.to_h do |path|
  [path, Links.extract(File.read(File.join(ROOT, path))).select { |u| Links.checkable?(u) }]
end
queue = Queue.new
urls_by_article.values.flatten.uniq.each { |u| queue << u }
results = {}
lock = Mutex.new
Array.new(THREADS) do
  Thread.new do
    while (url = (queue.pop(true) rescue nil))
      check = Links.check(url)
      lock.synchronize { results[url] = check }
    end
  end
end.each(&:join)

report = urls_by_article.map do |path, urls|
  checks = urls.map { |u| results.fetch(u) }
  { path: path, broken: checks.select { |c| c.verdict == :broken }.map(&:to_h),
    unverified: checks.select { |c| c.verdict == :unverified }.map(&:to_h), checked: checks.size }
end
broken = report.sum { |r| r[:broken].size }

if json
  puts JSON.pretty_generate(ok: broken.zero?, broken: broken, articles: report)
else
  puts "No changed articles." if articles.empty?
  report.each do |r|
    next if r[:broken].empty? && r[:unverified].empty?

    puts r[:path]
    r[:broken].each { |c| puts "  error:   #{c[:url]} — #{c[:detail]}" }
    r[:unverified].each { |c| puts "  warning: #{c[:url]} — could not verify (#{c[:detail]})" }
  end
  puts "#{results.size} external links in #{articles.size} articles: #{broken} broken"
end

exit(broken.zero? ? 0 : 1)
