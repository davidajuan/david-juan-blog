require 'fileutils'

# Remove all .html ext of posts, for pretty url and S3 restriction
# Production only

Jekyll::Hooks.register :posts, :post_write do |post|
  if Jekyll.env == 'production'
    path = post.destination('/')
    FileUtils.mv(path, path.sub(/\.html$/, ''))
  end
end