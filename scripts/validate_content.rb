#!/usr/bin/env ruby
# frozen_string_literal: true

# Validate every article against the content contract (docs/content-authoring.md).
#
#   ruby scripts/validate_content.rb                 # all articles
#   ruby scripts/validate_content.rb content/posts/my-article
#   ruby scripts/validate_content.rb --json          # machine-readable output
#
# Exit status: 0 = no errors (warnings allowed), 1 = at least one error.

require "json"
require_relative "../_plugins/content_contract"

root = ENV.fetch("BLOG_ROOT", File.expand_path("..", __dir__))
json = ARGV.delete("--json")
targets = ARGV.map { |a| File.expand_path(a) }

results = TechBlog::ContentContract.validate_all(root)
unless targets.empty?
  results = results.select do |r|
    full = File.join(root, r.path)
    targets.any? { |t| full == t || full.start_with?("#{t.chomp('/')}/") }
  end
  if results.empty?
    warn "No articles found at: #{ARGV.join(', ')}"
    exit 1
  end
end

errors = results.sum { |r| r.errors.size }
warnings = results.sum { |r| r.warnings.size }

if json
  puts JSON.pretty_generate(
    ok: errors.zero?,
    errors: errors,
    warnings: warnings,
    articles: results.reject { |r| r.errors.empty? && r.warnings.empty? }.map(&:to_h)
  )
else
  results.each do |r|
    next if r.errors.empty? && r.warnings.empty?

    puts r.path
    r.errors.each { |e| puts "  error:   #{e}" }
    r.warnings.each { |w| puts "  warning: #{w}" }
  end
  puts "#{results.size} articles checked: #{errors} errors, #{warnings} warnings"
end

exit(errors.zero? ? 0 : 1)
