# How to write a blog

It's easy to publish a post to github page in hugo framework and this is an
example. But there are some points worthing a notice.
* avoid capacity character in directory name
* use `date '+%Y-%m-%d' | awk '{print $1 ".md"}' | xargs hugo new` to generate a new post

# Common-used commands
* get current time `date '+%Y-%m-%d %H:%M:%S %z'`