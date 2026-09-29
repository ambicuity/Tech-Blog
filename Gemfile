source "https://rubygems.org"

gem "jekyll", "~> 4.3"

# The theme is maintained in-repo (_layouts, _includes, _sass, _plugins).
# Standard libraries that are no longer default gems on Ruby 3.4+.
gem "csv"
gem "logger"
gem "base64"
gem "bigdecimal"

group :jekyll_plugins do
  gem "jekyll-paginate"
  gem "jekyll-sitemap"
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
  gem "jekyll-archives"
end

# Windows and JRuby does not include zoneinfo files, so bundle the tzinfo-data gem
# and associated library.
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.1", :platforms => [:mingw, :x64_mingw, :mswin]

# Lock `http_parser.rb` gem to `v0.6.x` on JRuby builds since newer versions of the gem
# do not have a Java counterpart.
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]

# GitHub Pages compatibility
gem "webrick", "~> 1.8"

# Site testing
gem "html-proofer", "~> 5.0"
gem "minitest", "~> 5.25"
