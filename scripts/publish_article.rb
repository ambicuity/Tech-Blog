#!/usr/bin/env ruby
# frozen_string_literal: true

# Create an article bundle from a structured JSON package. This is the
# intended entry point for automated authors (e.g. Muse): they produce JSON,
# this script produces a valid content/posts/<slug>/ folder, or nothing.
#
#   ruby scripts/publish_article.rb article.json            # create the bundle
#   ruby scripts/publish_article.rb article.json --dry-run  # validate only
#   ruby scripts/publish_article.rb article.json --force    # replace an existing bundle
#   ruby scripts/publish_article.rb article.json --json     # machine-readable result
#
# The JSON format is documented in docs/content-authoring.md ("Publishing from
# JSON"). Exit status 0 = bundle written and valid; 1 = rejected (nothing kept).

require "base64"
require "fileutils"
require "json"
require "time"
require "tmpdir"
require "yaml"
require_relative "../_plugins/content_contract"

# BLOG_ROOT lets tests point the script at a scratch copy of the repository.
ROOT = ENV.fetch("BLOG_ROOT", File.expand_path("..", __dir__))
Contract = TechBlog::ContentContract

args = ARGV.dup
dry_run = args.delete("--dry-run")
force = args.delete("--force")
json_out = args.delete("--json")
package_path = args.first

def finish(ok, payload, json_out)
  if json_out
    puts JSON.pretty_generate(payload.merge(ok: ok))
  else
    puts(ok ? "OK  #{payload[:path]} -> #{payload[:url]}" : "REJECTED")
    Array(payload[:errors]).each { |e| puts "  error:   #{e}" }
    Array(payload[:warnings]).each { |w| puts "  warning: #{w}" }
  end
  exit(ok ? 0 : 1)
end

abort "usage: ruby scripts/publish_article.rb article.json [--dry-run] [--force] [--json]" unless package_path

package = begin
  JSON.parse(File.read(package_path))
rescue Errno::ENOENT, JSON::ParserError => e
  finish(false, { errors: ["cannot read package: #{e.message}"] }, json_out)
end
finish(false, { errors: ["package must be a JSON object"] }, json_out) unless package.is_a?(Hash)

problems = []
%w[title description content].each do |key|
  problems << "#{key} is required" if package[key].to_s.strip.empty?
end
%w[categories tags].each do |key|
  problems << "#{key} must be a non-empty array" unless package[key].is_a?(Array) && !package[key].empty?
end
known = %w[title slug description date updated author categories tags kind featured draft cover canonical_url content images]
unknown = package.keys - known
problems << "unknown fields: #{unknown.join(', ')}" unless unknown.empty?
finish(false, { errors: problems }, json_out) unless problems.empty?

slug = (package["slug"] || Contract.slugify(package["title"])).to_s
date = package["date"] ? Contract.to_time(package["date"]) : Time.now.utc
finish(false, { errors: ["date '#{package['date']}' is not a valid date"] }, json_out) unless date

front = {
  "title" => package["title"].to_s.strip,
  "description" => package["description"].to_s.strip,
  "date" => date.utc.strftime("%Y-%m-%d %H:%M:%S +0000"),
  "updated" => package["updated"] && Contract.to_time(package["updated"])&.utc&.strftime("%Y-%m-%d %H:%M:%S +0000"),
  "author" => package["author"] || "ritesh",
  "categories" => package["categories"],
  "tags" => package["tags"],
  "kind" => package["kind"],
  "featured" => package["featured"],
  "draft" => package.key?("draft") ? package["draft"] : false,
  "cover" => package["cover"],
  "canonical_url" => package["canonical_url"]
}.compact

body = package["content"].to_s.strip
document = "#{YAML.dump(front).sub(/\A---\n/, "---\n")}---\n\n#{body}\n"

target = File.join(ROOT, "content", "posts", slug)
if File.exist?(target) && !force
  finish(false, { slug: slug, errors: ["content/posts/#{slug} already exists (use --force to replace it)"] }, json_out)
end

# Assemble in a scratch copy of the repository's content tree so validation
# (including duplicate-slug checks) sees the final state before anything is kept.
Dir.mktmpdir("publish-article") do |tmp|
  %w[_data _posts content].each do |d|
    src = File.join(ROOT, d)
    FileUtils.cp_r(src, tmp) if File.exist?(src)
  end
  staged = File.join(tmp, "content", "posts", slug)
  FileUtils.rm_rf(staged)
  FileUtils.mkdir_p(staged)
  File.write(File.join(staged, "index.md"), document)

  base = File.dirname(File.expand_path(package_path))
  Array(package["images"]).each do |image|
    name = image["name"].to_s
    if name.empty? || name.include?("..") || name.start_with?("/")
      finish(false, { slug: slug, errors: ["image name '#{name}' must be a relative file name"] }, json_out)
    end
    dest = File.join(staged, name)
    FileUtils.mkdir_p(File.dirname(dest))
    if image["base64"]
      File.binwrite(dest, Base64.decode64(image["base64"]))
    elsif image["path"]
      src = File.expand_path(image["path"], base)
      finish(false, { slug: slug, errors: ["image file not found: #{image['path']}"] }, json_out) unless File.file?(src)
      FileUtils.cp(src, dest)
    else
      finish(false, { slug: slug, errors: ["image '#{name}' needs either path or base64"] }, json_out)
    end
  end

  results = Contract.validate_all(tmp)
  result = results.find { |r| r.path == "content/posts/#{slug}/index.md" }
  payload = {
    slug: slug,
    path: "content/posts/#{slug}/index.md",
    url: "/posts/#{slug}/",
    draft: front["draft"],
    errors: result.errors,
    warnings: result.warnings
  }
  finish(false, payload, json_out) unless result.ok?

  unless dry_run
    FileUtils.rm_rf(target)
    FileUtils.mkdir_p(File.dirname(target))
    FileUtils.cp_r(staged, target)
  end
  finish(true, payload.merge(dry_run: !dry_run.nil?), json_out)
end
