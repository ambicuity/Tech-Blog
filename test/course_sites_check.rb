# frozen_string_literal: true

# Checks that _data/course_sites.yml matches the live course sites: each URL
# answers 200 and its <meta name="description"> ("421 lessons. 20 phases. …")
# reports the same lesson/phase counts.
#
#   bundle exec ruby test/course_sites_check.rb
#
# Deliberately NOT part of CI: it depends on three external sites, and a
# deploy of this blog should never fail because one of them is down.

require "net/http"
require "uri"
require "yaml"

ROOT = File.expand_path("..", __dir__)
courses = YAML.safe_load_file(File.join(ROOT, "_data", "course_sites.yml"))

def fetch(url, limit = 3)
  response = Net::HTTP.get_response(URI(url))
  return fetch(response["location"], limit - 1) if response.is_a?(Net::HTTPRedirection) && limit.positive?

  response
end

failures = courses.filter_map do |course|
  response = fetch(course["url"])
  next "#{course['title']}: HTTP #{response.code} from #{course['url']}" unless response.is_a?(Net::HTTPSuccess)

  description = response.body[/<meta name="description" content="([^"]*)"/, 1].to_s
  lessons = description[/(\d+)\s+lessons/, 1]&.to_i
  phases = description[/(\d+)\s+phases/, 1]&.to_i
  next "#{course['title']}: could not read counts from #{course['url']}" unless lessons && phases

  mismatch = []
  mismatch << "lessons #{course['lessons']} -> #{lessons}" if lessons != course["lessons"]
  mismatch << "phases #{course['phases']} -> #{phases}" if phases != course["phases"]
  "#{course['title']}: update _data/course_sites.yml (#{mismatch.join(', ')})" unless mismatch.empty?
rescue SocketError, SystemCallError, Net::OpenTimeout, Net::ReadTimeout => e
  "#{course['title']}: #{e.class}: #{e.message}"
end

if failures.empty?
  puts "course_sites.yml matches all #{courses.size} live course sites"
else
  warn failures.join("\n")
  exit 1
end
